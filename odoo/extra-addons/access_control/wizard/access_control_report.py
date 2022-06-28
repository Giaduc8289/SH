# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class AccessControlReportWizard(models.TransientModel):
    _name = 'access.control.report.wizard'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    purpose = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('visit', 'Visit'), ('work', 'Work')],
                               'Purpose')
    res_partner_id = fields.Many2one("res.partner", "Partner", domain="[('code', '!=', None)]")

    def get_report(self):
        date_start = self.date_start
        date_end = self.date_end
        domain = []
        if self.date_start:
            domain = expression.AND([domain, [('in_time', '>=', self.date_start)]])
            date_start = date_start.strftime('%d/%m/%Y')
        if self.date_end:
            domain = expression.AND([domain, [('in_time', '<=', self.date_end)]])
            date_end = date_end.strftime('%d/%m/%Y')
        if self.purpose:
            domain = expression.AND([domain, [('purpose', '=', self.purpose)]])
        if self.res_partner_id:
            domain = expression.AND([domain, [('res_partner_id.code', '=', self.res_partner_id.code)]])

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': date_start, 'date_end': date_end, 'purpose': self.purpose, 'res_partner_id': self.res_partner_id.name, 'domain': domain
            },
        }

        action = self.env.ref('access_control.action_report_access_control').report_action(self, data=data)
        return action


class ReportAccessControl(models.AbstractModel):
    _name = 'report.access_control.report_access_control_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        purpose = data['form']['purpose']
        res_partner_id = data['form']['res_partner_id']
        domain = data['form']['domain']

        data_ac = self.env['access.control'].search(domain)
        docs = self.env['access.control'].browse(data_ac.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'purpose': purpose,
            'res_partner_id': res_partner_id,
            'docs': docs,
        }

