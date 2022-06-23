# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import Counter, defaultdict

from odoo import _, api, fields, tools, models
from odoo.odoo.osv import expression

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _description = "Product Moves (Stock Move Line)"

    manufacturing_date = fields.Datetime('Date', default=fields.Datetime.now, required=True)

    def action_alarm_data(self):
        action = self.env["ir.actions.actions"]._for_xml_id('stock_inheritance.action_stock_alarm')
        domain = []
        if self.location_dest_id:
            domain = expression.AND([domain, [('location_dest_id', '=', self.location_dest_id.name)]])
        action['domain'] = domain
        return action
