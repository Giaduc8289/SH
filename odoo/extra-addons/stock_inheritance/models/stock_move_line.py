# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import Counter, defaultdict

from odoo import _, api, fields, tools, models
from odoo.osv import expression


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _description = "Product Moves (Stock Move Line)"

    manufacturing_date = fields.Datetime('Manufacturing Date')

class FilterAlarmStock(models.Model):
    _name = 'filter.alarm.stock'
    _description = "Alarm Stock"

    location_dest_id = fields.Many2one('stock.location', 'To', domain="[('usage', '!=', 'view')]", check_company=True, required=True)
    def action_alarm_data(self):
        action = self.env["ir.actions.actions"]._for_xml_id('stock_inheritance.action_stock_alarm')
        domain = []
        if self.location_dest_id:
            domain = expression.AND([domain, [('location_dest_id', '=', self.location_dest_id.id)]])
        action['domain'] = domain
        return action
