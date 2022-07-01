# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _order = "product_id"

    product_default_code = fields.Char(related="product_template_id.default_code", string="Mã hàng")
    product_weight = fields.Float(related="product_template_id.weight", string="Quy cách")
    amount_package = fields.Integer(string='Số bao')

    @api.onchange("amount_package")
    def _amount_package(self):
        for record in self:
            if (record.product_weight == 0):
                record.amount_package = 0
            else:
                record.product_uom_qty = int(record.amount_package * record.product_weight)

    def _get_display_price(self, product):
        pricelist_item = self.order_id.pricelist_id.id
        data = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_item)
                                                             , ('product_tmpl_id', '=', product.id)], limit=1)
        if data:
            base_price, currency = data[0].final_price, data[0].currency_id
            final_price = data[0].final_price
        return max(base_price, final_price)