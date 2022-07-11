# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_id = fields.Many2one("product.product", "Product", domain="[('categ_id', 'in', (10, 11, 12))]")
