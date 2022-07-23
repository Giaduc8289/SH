# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast

from odoo import fields, models, api,  _
from odoo.exceptions import ValidationError

class CouponProgram(models.Model):
    _inherit = 'coupon.program'
    _description = "Coupon Program"

    config_detail = fields.Boolean(string='Cấu hình chi tiết', default=False)
    coupon_detail_ids = fields.One2many('coupon.detail', 'program_id', string="Chiết khấu chi tiết")

    coupon_partner_ids = fields.Many2many('res.partner', column1='coupon_program_id', column2='code',
                                            relation='coupon_program_res_partner_rel', string="Khách hàng",
                                            domain="[('code', 'like', 'KH%')]")
    coupon_products_ids = fields.Many2many('product.template', column1='coupon_program_id', column2='id',
                                            relation='coupon_program_product_template_rel', string="Sản phẩm")
    payment_type = fields.Selection([('later', 'Pay later'), ('now', 'Pay now')], string="Payment_type", default='now')
    shortened_name = fields.Many2one('ir.model.fields', string="Shortened name", domain="[('model', '=', 'partner.coupon.wizard')]")

    
    def _is_valid_partner(self, partner):
        if self.coupon_partner_ids:
            domain = [('id', 'in', self.coupon_partner_ids.ids), ('id', '=', partner.id)]
            return bool(self.env['res.partner'].search_count(domain))
        else:
            return True

    def _get_valid_products(self, products):
        if self.coupon_products_ids:
            domain = [('id', 'in', self.coupon_products_ids.ids)]
            return products.filtered_domain(domain)
        return products

    def _get_discount_product_values(self):
        return {
            'name': self.reward_id.display_name,
            'type': 'service',
            'taxes_id': False,
            'supplier_taxes_id': False,
            'sale_ok': False,
            'purchase_ok': False,
            'lst_price': 0, #Do not set a high value to avoid issue with coupon code
        }

    def _keep_only_most_interesting_auto_applied_global_discount_program(self):
        '''Given a record set of programs, remove the less interesting auto
        applied global discount to keep only the most interesting one.
        We should not take promo code programs into account as a 10% auto
        applied is considered better than a 50% promo code, as the user might
        not know about the promo code.
        '''
        #--------- bỏ xét lấy chương trình giảm giá tốt nhất

        programs = self.filtered(lambda p: p._is_global_discount_program() and p.promo_code_usage == 'no_code_needed')
        if not programs: return self
        return self

    def _check_promo_code(self, order, coupon_code):
        message = {}
        if self.maximum_use_number != 0 and self.total_order_count >= self.maximum_use_number:
            message = {'error': _('Promo code %s has been expired.') % (coupon_code)}
        elif not self._filter_on_mimimum_amount(order):
            message = {'error': _(
                'A minimum of %(amount)s %(currency)s should be purchased to get the reward',
                amount=self.rule_minimum_amount,
                currency=self.currency_id.name
            )}
        elif self.promo_code and self.promo_code == order.promo_code:
            message = {'error': _('The promo code is already applied on this order')}
        # elif self in order.no_code_promo_program_ids:
        #     message = {'error': _('The promotional offer is already applied on this order')}
        elif not self.active:
            message = {'error': _('Promo code is invalid')}
        elif self.rule_date_from and self.rule_date_from > fields.Datetime.now():
            tzinfo = self.env.context.get('tz') or self.env.user.tz or 'UTC'
            locale = self.env.context.get('lang') or self.env.user.lang or 'en_US'
            message = {'error': _('This coupon is not yet usable. It will be starting from %s') % (format_datetime(self.rule_date_from, format='short', tzinfo=tzinfo, locale=locale))}
        elif self.rule_date_to and fields.Datetime.now() > self.rule_date_to:
            message = {'error': _('Promo code is expired')}
        elif order.promo_code and self.promo_code_usage == 'code_needed':
            message = {'error': _('Promotionals codes are not cumulative.')}
        # elif self._is_global_discount_program() and order._is_global_discount_already_applied():
        #     message = {'error': _('Global discounts are not cumulative.')}
        elif self.promo_applicability == 'on_current_order' and self.reward_type == 'product' and not order._is_reward_in_order_lines(self):
            message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}
        elif not self._is_valid_partner(order.partner_id):
            message = {'error': _("The customer doesn't have access to this reward.")}
        elif not self._filter_programs_on_products(order):
            message = {'error': _("You don't have the required product quantities on your sales order. If the reward is same product quantity, please make sure that all the products are recorded on the sales order (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free'.")}
        elif self.promo_applicability == 'on_current_order' and not self.env.context.get('applicable_coupon'):
            applicable_programs = order._get_applicable_programs()
            if self not in applicable_programs:
                message = {'error': _('At least one of the required conditions is not met to get the reward!')}
        return message