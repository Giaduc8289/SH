import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class EmployeeDepartmentInfo(models.Model):
    _inherit = ['hr.department']
    _log_access = False

    code = fields.Char(string="Code", readonly=True, required=True, copy=False, default='D000')

    @api.model
    def create(self, vals):
        if vals.get('code', 'D000') == 'D000':
            seq = self.env.ref('employee_management.department_code_object_sequence')
            vals['code'] = seq.next_by_id() or 'D000'
        result = super(EmployeeDepartmentInfo, self).create(vals)
        return result
