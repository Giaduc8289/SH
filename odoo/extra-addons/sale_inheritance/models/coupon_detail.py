# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CouponDetail(models.Model):
    _name = 'coupon.detail'
    _description = "Coupon Detail"

    discount_fixed_amount_detail = fields.Float(string='Giá trị chiết khấu', default=0)
    discount_hold_amount_detail = fields.Float(string='Giá trị giữ lại', default=0)
    discount_percentage_detail = fields.Float(string="Phần trăm chiết khấu", default=10, help='The discount in percentage, between 1 and 100')

    program_id = fields.Many2one('coupon.program', string="Chương trình chiết khấu")
    partner_ids = fields.Many2many('res.partner', column1='partner_id', column2='program_id', relation='coupon_program_partner_rel', string="Khách hàng")

    @api.constrains('discount_hold_amount_detail')
    def _check_discount_hold_amount_detail(self):
        for record in self:
            if record.discount_hold_amount_detail < 0 or record.discount_hold_amount_detail > record.discount_fixed_amount_detail:
                raise ValidationError("Discount hold amount in 0 to {}".format(record.discount_fixed_amount_detail))
