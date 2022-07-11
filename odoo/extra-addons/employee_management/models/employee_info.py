import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class EmployeeInfo(models.Model):
    _inherit = ["hr.employee"]
    _log_access = False
    address_2 = fields.Char(string="Home number")
    phone_2 = fields.Char(string="Phone 2")
    start_date = fields.Datetime('Start date')
    end_date = fields.Datetime('End date')
    type_contract = fields.Selection(
        [('DH', 'Unlimited time'), ('NH', 'Limited time'), ('TV', 'Part time')],
        'Type of contract')
    certificate = fields.Selection([
        ('doctor', 'Doctor'),
        ('master', 'Master'),
        ('bachelor', 'Bachelor'),
        ('vocational', 'Vocational training centers'),
        ('graduate', 'Graduate'),
        ('other', 'Other'),
    ], 'Certificate Level', default='graduate', groups="hr.group_hr_user", tracking=True)
    image_upload = fields.Many2many('ir.attachment', string="Upload")
    @api.model
    def _default_country_id(self):
        vn = self.env['res.country'].search([('code', '=ilike', 'VN')])
        if vn:
            return vn.id
        return None

    country_id = fields.Many2one(default=lambda self: self._default_country_id())
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', required=True,
                               domain="[('country_id', '=?', country_id)]")
    state_ids = fields.Many2many("res.country.state", string='State', relation="employee_state_rel",
                                 column1='employee_id',
                                 column2='state_id',
                                 domain="[('country_id', '=?', country_id)]")

    district_id = fields.Many2one("res.country.location", string='District', ondelete='restrict',
                                  domain="[('state_id', '=?', state_id), ('location_type', '=', 'dist')]")

    village_id = fields.Many2one("res.country.location", string='Village', ondelete='restrict',
                                 domain="[('parent_id', '=?', district_id), ('location_type', '=', 'ward')]")

    country_code = fields.Char(related='country_id.code', string="Country Code")

    hide = fields.Boolean(string='Hide', compute="_compute_hide")

    # Show Hide State selection based on Country
    @api.depends('country_id')
    def _compute_hide(self):
        if self.country_id:
            self.hide = False
        else:
            self.hide = True

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id
            self.district_id = False
            self.village_id = False

    @api.onchange('district_id')
    def _onchange_district(self):
        if self.district_id:
            self.district_id = self.district_id
            self.village_id = False

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(state_code)s %(zip)s\n%(country_name)s"

    @api.model
    def _get_address_format(self):
        return self.country_id.address_format or self._get_default_address_format()

    @api.model
    def _formatting_address_fields(self):
        """Returns the list of address fields usable to format addresses."""
        return self._address_fields()

    def _get_country_name(self):
        return self.country_id.name or ''

    def _prepare_display_address(self, without_company=False):
        # get the information that will be injected into the display format
        # get the address format
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        return address_format, args

    def _display_address(self, without_company=False):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param without_company: if address contains company
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        address_format, args = self._prepare_display_address(without_company)
        return address_format % args
