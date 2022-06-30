# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools import populate
from datetime import timedelta, date

class Pricelist(models.Model):
    _inherit = "product.pricelist"

    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Discount'),
        ('formula', 'Formula')], index=True, default='fixed', required=True)
    base = fields.Selection([
        ('list_price', 'Sales Price'),
        ('standard_price', 'Cost'),
        ('pricelist', 'Other Pricelist')], "Based on",
        default='list_price', required=True,
        help='Base price for computation.\n'
             'Sales Price: The base price will be the Sales Price.\n'
             'Cost Price : The base price will be the cost price.\n'
             'Other Pricelist : Computation of the base price based on another Pricelist.')
    base_pricelist_id = fields.Many2one('product.pricelist', 'Other Pricelist', check_company=True)
    date_start = fields.Datetime('Start Date', help="Starting datetime for the pricelist item validation\n"
                                                "The displayed value depends on the timezone set in your preferences.")
    date_end = fields.Datetime('End Date', help="Ending datetime for the pricelist item validation\n"
                                                "The displayed value depends on the timezone set in your preferences.")

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    discount_month = fields.Float('Discount Month')
    discount_year = fields.Float('Discount Year')
    reduce_direct = fields.Float('Reduce Direct')
    bonus_quantity = fields.Float('Bonus Quantity')
    support_shipping = fields.Float('Support Shipping')
    support_new_agency = fields.Float('Support New Agency')
    reduce_loss = fields.Float('Reduce Loss')

