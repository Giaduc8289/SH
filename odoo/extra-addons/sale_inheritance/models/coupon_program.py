# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import ast

from odoo import fields, models, api
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
    shortened_name = fields.Char(string="Shortened name")
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

