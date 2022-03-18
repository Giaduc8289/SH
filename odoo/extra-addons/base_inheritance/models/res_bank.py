from odoo import models, api, fields


class Bank(models.Model):
    _inherit = 'res.bank'

    @api.model
    def _default_country_id(self):
        vn = self.env['res.country'].search([('code', '=ilike', 'VN')])
        if vn:
            return vn.id
        return None

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self._default_country_id())
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    district_id = fields.Many2one("res.country.location", string='District', ondelete='restrict',
                                  domain="[('state_id', '=?', state_id), ('location_type', '=', 'dist')]")
    village_id = fields.Many2one("res.country.location", string='Village', ondelete='restrict',
                                 domain="[('parent_id', '=?', district_id), ('location_type', '=', 'ward')]")
    street = fields.Char()


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch_name = fields.Char('Branch name')
    description = fields.Char('Description')

    @api.model
    def _default_country_id(self):
        vn = self.env['res.country'].search([('code', '=ilike', 'VN')])
        if vn:
            return vn.id
        return None

    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=lambda self: self._default_country_id())
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    district_id = fields.Many2one("res.country.location", string='District', ondelete='restrict',
                                  domain="[('state_id', '=?', state_id), ('location_type', '=', 'dist')]")
    village_id = fields.Many2one("res.country.location", string='Village', ondelete='restrict',
                                 domain="[('parent_id', '=?', district_id), ('location_type', '=', 'ward')]")
    street = fields.Char()
