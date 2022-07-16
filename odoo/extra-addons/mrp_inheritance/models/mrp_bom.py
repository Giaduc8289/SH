# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS
from odoo.tools import float_round

from collections import defaultdict


class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',
        check_company=True, index=True,
        domain="[('categ_id', 'in', (10, 11, 12))]", required=True)
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        check_company=True, index=True,
        domain="[('categ_id', 'in', (10, 11, 12))]",
        help="If a product variant is defined the BOM is available only for this product.")

