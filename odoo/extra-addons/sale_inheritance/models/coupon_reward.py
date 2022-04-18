# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CouponReward(models.Model):
    _inherit = 'coupon.reward'
    _description = "Coupon Reward"

    discount_for_amount = fields.Boolean(string='Discount for amount', default=True)
    discount_hold_amount = fields.Float(string='Discount hold amount', default=0)
    discount_hold_time = fields.Selection([('month', 'Month'), ('quarter', 'Quarter'), ('year', 'Year')], 'Discount hold time', default='year')

    @api.constrains('discount_hold_amount')
    def _check_discount_hold_amount(self):
        for record in self:
            if record.discount_hold_amount < 0 or record.discount_hold_amount > record.discount_fixed_amount:
                raise ValidationError("Discount hold amount in 0 to {}".format(record.discount_fixed_amount))
