# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CouponProgram(models.Model):
    _inherit = 'coupon.program'
    _description = "Coupon Program"

    config_detail = fields.Boolean(string='Cấu hình chi tiết', default=False)
    coupon_detail_ids = fields.One2many('coupon.detail', 'program_id', string="Chiết khấu chi tiết")
