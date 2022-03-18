# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CountryLocation(models.Model):
    _name = "res.country.location"
    _description = "District & Wards"
    _order = 'code'

    code = fields.Char(string="Location's Code", index=True)
    name = fields.Char(string="Location's Name", required=True, index=True)
    state_id = fields.Many2one('res.country.state', 'State', required=True, index=True)
    country_id = fields.Many2one(related='state_id.country_id', store=True)
    location_type = fields.Selection([('dist', 'District'), ('ward', 'Wards')], string='Location Type', default='dist',
                                     required=True)
    active = fields.Boolean('Active', default=True, store=True, readonly=False)

    parent_id = fields.Many2one('res.country.location', string='District', index=True)
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')
    child_ids = fields.One2many('res.country.location', 'parent_id', string='Ward', domain=[('active', '=', True)])
    note = fields.Text(string='Note')

    _sql_constraints = [
        ('name_code_uniq', 'unique(state_id, code)', 'The code of the location must be unique by State !')
    ]

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        self.ensure_one()
        if self.parent_id:
            self.location_type = 'ward'
            self.state_id = self.parent_id.state_id
            self.country_id = self.parent_id.country_id
