# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CouponReward(models.Model):
    _inherit = 'coupon.reward'
    _description = "Coupon Reward"

    discount_for_amount = fields.Boolean(string='Discount for amount', default=True)
    discount_hold_time = fields.Selection([('month', 'Month'), ('quarter', 'Quarter'), ('year', 'Year')], 'Discount hold time', default='year')

