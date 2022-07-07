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
    date_start = fields.Date(string="Date start")
    date_end = fields.Date(string="Date end")
    payment_type = fields.Selection([('later', 'Pay later'), ('now', 'Pay now')], 'Kiểu thanh toán', default='now')
    from_date = fields.Date(string="From date")
    to_date = fields.Date(string="To date")
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


