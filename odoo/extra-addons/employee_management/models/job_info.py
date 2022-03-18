import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class EmployeeJobInfo(models.Model):
    _inherit = ['hr.job']
    _log_access = False

    code = fields.Char(string="Code", readonly=True, required=True, copy=False, default='P000')
    active = fields.Boolean('Active', default=True)

    @api.model
    def create(self, vals):
        if vals.get('code', 'P000') == 'P000':
            seq = self.env.ref('employee_management.job_code_object_sequence')
            vals['code'] = seq.next_by_id() or 'P000'
        result = super(EmployeeJobInfo, self).create(vals)
        return result
