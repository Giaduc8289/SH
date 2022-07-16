# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class PostpaidDiscountReportWizard(models.TransientModel):
    _name = 'postpaid.discount.wizard'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    khachhang = fields.Many2one("res.partner", "Khách hàng", domain="[('code', 'like', 'KH%')]")


    def get_report(self):
        date_start = self.date_start
        date_end = self.date_end
        domain = []
        if self.date_start:
            domain = expression.AND([domain, [('date_order', '>=', self.date_start)]])
            date_start = date_start.strftime('%d/%m/%Y')
        if self.date_end:
            domain = expression.AND([domain, [('date_order', '<=', self.date_end)]])
            date_end = date_end.strftime('%d/%m/%Y')
        if self.khachhang:
            domain = expression.AND([domain, [('partner_id.code', '=', self.khachhang.code)]])
        domain = expression.AND([domain, [('invoice_status', 'in', ('invoiced', 'to invoice'))]])

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': date_start, 'date_end': date_end, 'khachhang': self.khachhang.name,  'domain': domain,
            },
        }
        action = self.env.ref('sale_inheritance.action_report_postpaid_discount').report_action(self, data=data)
        return action
class PostpaidDiscount(models.AbstractModel):
    _name = 'report.sale_inheritance.report_postpaid_discount_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        khachhang = data['form']['khachhang']
        domain = data['form']['domain']

        data_sa = self.env['sale.order'].search(domain)
        docs = self.env['sale.order'].browse(data_sa.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'khachhang': khachhang,
            'docs': docs,
        }

