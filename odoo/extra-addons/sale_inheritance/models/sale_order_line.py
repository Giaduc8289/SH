# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _order = "product_id"

    product_default_code = fields.Char(related="product_template_id.default_code", string="Mã hàng")
    product_weight = fields.Float(related="product_template_id.weight", string="Quy cách")

    amount_package = fields.Integer(string='Số lượng (bao)', compute="_amount_package")

    @api.depends("product_uom_qty")
    def _amount_package(self):
        for record in self:
            if record.product_weight == 0:
                record.amount_package = 0
                continue
            record.amount_package = int(record.product_uom_qty / record.product_weight)

