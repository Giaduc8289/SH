from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _default_country_id(self):
        vn = self.env['res.country'].search([('code', '=ilike', 'VN')])
        if vn:
            return vn.id
        return None

    code = fields.Char(string='Code')
    group_customer = fields.Selection([('agency', 'Agency'), ('farm', 'Farm'), ('both', 'Both')], 'Group of customer',
                                      default='agency')
    country_id = fields.Many2one(default=lambda self: self._default_country_id())
    district_id = fields.Many2one("res.country.location", string='District', ondelete='restrict',
                                  domain="[('state_id', '=?', state_id), ('location_type', '=', 'dist')]")
    village_id = fields.Many2one("res.country.location", string='Village', ondelete='restrict',
                                 domain="[('parent_id', '=?', district_id), ('location_type', '=', 'ward')]")
    date_open_book = fields.Date(string='Date open code book')

    @api.model
    def create(self, vals_list):
        data = super(ResPartner, self).create(vals_list)
        if data.supplier_rank > 0:
            seq = self.env.ref('base_inheritance.sequence_code_supplier')
            data.code = seq.next_by_id() or 'NCC'
        elif data.customer_rank > 0:
            seq = self.env.ref('base_inheritance.sequence_code_customer')
            data.code = seq.next_by_id() or 'KH'
        return data
