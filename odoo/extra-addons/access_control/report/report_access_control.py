# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ReportAccessControl(models.Model):
    _name = 'report.access.control'
    _auto = False
    _description = 'Access Control Report'

    f_date = fields.Date('From date')
    t_date = fields.Date('To date')
    purpose = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('visit', 'Visit'), ('work', 'Work')],
                               'Purpose')
    res_partner_id = fields.Many2one("res.partner", "Partner", domain="[('code', '!=', None)]")

    name = fields.Char('Name', readonly=True)
    address = fields.Char('Address', readonly=True)
    number_plate = fields.Char('Number plate', readonly=True)
    in_time = fields.Datetime('In time', readonly=True)
    ordinal_number = fields.Integer('Ordinal number', readonly=True)
    out_time = fields.Datetime('Out time', readonly=True)

    weight_in = fields.Float('Weight in', readonly=True)
    weight_out = fields.Float('Weight out', readonly=True)

    purpose_descript = fields.Char('Purpose descript', readonly=True)
    state = fields.Selection([
        ('in', 'In'),
        ('weighin', 'Vehicle Weigh In'),
        ('unload', 'Unload Goods'),
        ('weighout', 'Vehicle Weigh Out'),
        ('out', 'Out'),
    ], string='Status', readonly=True)

    def action_print(self):
        action = self.get_access_action('report_access_control_action')
        return action

    def init(self):
        self.purpose = 'sale'
        tools.drop_view_if_exists(self._cr, 'report_access_control')
        query = """
CREATE or REPLACE VIEW report_access_control AS (
SELECT
    id AS id, purpose, res_partner_id, name, address, number_plate
    , in_time, out_time, weight_in, weight_out, state, ordinal_number, purpose_descript
    , in_time::date AS f_date
    , out_time::date AS t_date
FROM access_control ac
WHERE (purpose = '%s' OR %s = False)
ORDER BY ordinal_number
);
""" % (self.purpose, self.purpose)
        self.env.cr.execute(query)



