# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class StockEntryReportWizard(models.TransientModel):
    _name = 'stock.entry.report.wizard'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    stock = fields.Many2one("stock.location", "Kho", domain="['&', ('id', '!=', None), ('usage', '!=', 'view')]")

    def get_report(self):
        domain = []
        if self.date_start:
            domain = expression.AND([domain, [('date', '>=', self.date_start)]])
        if self.date_end:
            domain = expression.AND([domain, [('date', '<=', self.date_end)]])
        if self.stock:
            domain = expression.AND([domain, ['|', ('location_id', '=', self.stock.id),
                                              ('location_dest_id', '=', self.stock.id)]])
        if self.stock:
            domain = expression.AND([domain, [('state', '=', 'done')]])
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': self.date_start, 'date_end': self.date_end, 'stock': self.stock.id, 'domain': domain
            },
        }

        action = self.env.ref('stock_inheritance.action_report_stock_entry').report_action(self, data=data)
        return action


class ReportStockEntry(models.AbstractModel):
    _name = 'report.stock_inheritance.report_stock_entry_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        stock = data['form']['stock']
        domain = data['form']['domain']

        data_sv = self.env['stock.move'].search(domain)
        docs = self.env['stock.move'].browse(data_sv.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'stock': stock,
            'docs': docs,
        }
