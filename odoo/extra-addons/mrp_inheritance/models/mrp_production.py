# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    product_id = fields.Many2one("product.product", "Product",
                                 domain="[('default_code', 'not like', 'BCA%'), '|', '|', ('default_code', 'like', 'CAVI%'), ('default_code', 'like', 'BN%'),('default_code', 'like', 'BC%')]")
