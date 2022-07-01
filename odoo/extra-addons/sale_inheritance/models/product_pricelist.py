# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools import populate
from datetime import timedelta, date


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        # ('percentage', 'Discount'),
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
    fixed_price = fields.Float('Fixed Price', digits='Product Price')
    final_price = fields.Float('Final Price', compute='_compute_final_price')

    @api.onchange('product_tmpl_id')
    def product_tmpl_id_change(self):
        if not self.product_tmpl_id:
            return
        if self.pricelist_id.base_pricelist_id:
            data = self.env['product.pricelist.item'].search([('pricelist_id', '=', self.pricelist_id.base_pricelist_id.ids)
                                                                 , ('product_tmpl_id', '=', self.product_tmpl_id.id)], limit=1)
            if data:
                vals = {}
                vals['fixed_price'] = data[0].fixed_price
                self.update(vals)

    @api.onchange('fixed_price','discount_month','discount_year','reduce_direct','bonus_quantity','support_shipping','support_new_agency','reduce_loss')
    def _compute_final_price(self):
        for item in self:
            item.final_price = item.fixed_price - item.discount_month - item.discount_year - item.reduce_direct - item.bonus_quantity - item.support_shipping - item.support_new_agency - item.reduce_loss

