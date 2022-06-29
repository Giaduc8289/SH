# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools import populate
from datetime import timedelta, date

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    discount_month = fields.Float('Discount Month')
    discount_year = fields.Float('Discount Year')
    reduce_direct = fields.Float('Reduce Direct')
    bonus_quantity = fields.Float('Bonus Quantity')
    support_shipping = fields.Float('Support Shipping')
    support_new_agency = fields.Float('Support New Agency')
    reduce_loss = fields.Float('Reduce Loss')

