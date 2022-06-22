# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import Counter, defaultdict

from odoo import _, api, fields, tools, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _description = "Product Moves (Stock Move Line)"

    manufacturing_date = fields.Datetime('Date', default=fields.Datetime.now, required=True)

    # def action_filter_data(self):
    #     return
