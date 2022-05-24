from odoo import _, fields, models, api, exceptions
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

class AccessControl(models.Model):
    _name = 'access.control'
    _description = "Access Control"
    _rec_name = 'res_partner_id'

    res_partner_id = fields.Many2one("res.partner", "Partner", domain="[('code', '!=', None)]")
    name = fields.Char('Name')
    address = fields.Char('Address')
    number_plate = fields.Char('Number plate')
    purpose = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('visit', 'Visit'), ('work', 'Work')], 'Purpose', default='purchase')
    in_time = fields.Datetime('In time', readonly=True, required=True, default=fields.Datetime.now)
    ordinal_number = fields.Integer('Ordinal number', default=0)
    out_time = fields.Datetime('Out time')

    weight_in = fields.Float('Weight in', default=0)
    weight_out = fields.Float('Weight out', default=0)

    product_template_ids = fields.Many2many('product.template', column1='product_template_id', column2='id', relation='access_control_product_template_rel', string="Products")
    purpose_descript = fields.Char('Purpose descript')

    state = fields.Selection([
        ('in', 'In'),
        ('weighin', 'Vehicle Weigh In'),
        ('unload', 'Unload Goods'),
        ('weighout', 'Vehicle Weigh Out'),
        ('out', 'Out'),
        ], string='Status', readonly=True, copy=False, index=True, default='in')

    @api.model
    def create(self, vals_list):
        if ('ordinal_number' in vals_list and vals_list['ordinal_number'] == 0) or 'ordinal_number' not in vals_list:
            seq = self.env.ref('access_control.sequence_ordinal_number_control_access')
            vals_list['ordinal_number'] = seq.next_by_id()
        return super(AccessControl, self).create(vals_list)

    @api.model
    def update_ordinal_number(self, data):
        seq = self.env.ref('access_control.sequence_ordinal_number_control_access')
        temp = self.browse(data)
        temp.ordinal_number = seq.next_by_id()

    def action_weigh_in(self):
        for record in self:
            if(record.state == 'in'):
                record.state = 'weighin'
                # form_view = [(self.env.ref('access_control.access_control_form_view').id, 'form')]

    def action_unload(self):
        for record in self:
            if(record.state == 'weighin'):
                record.state = 'unload'
            if(record.purpose == 'sale'):
                action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
            if(record.purpose == 'purchase'):
                action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        return action

    def action_purchase(self):
        action = self.env["ir.actions.actions"]
        for record in self:
            if(record.state == 'weighin'):
                record.state = 'unload'
            if ((record.state in ('weighin', 'unload')) and (record.purpose == 'sale')):
                action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        # if action is None:
        #     raise exceptions.UserError(_("No action available for this job"))
        return action

    def action_sale(self):
        action = self.env["ir.actions.actions"]
        for record in self:
            if(record.state == 'weighin'):
                record.state = 'unload'
            if ((record.state in ('weighin', 'unload')) and (record.purpose == 'purchase')):
                action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        # if action is None:
        #     raise exceptions.UserError(_("No action available for this job"))
        return action

    def action_weigh_out(self):
        for record in self:
            if(record.state == 'unload'):
                record.state = 'weighout'

    def action_check_out(self):
        for record in self:
            if(record.state != 'out'):
                record.out_time = fields.Datetime.now()
                record.state = 'out'

    @api.onchange('res_partner_id')
    def _compute_inf_partner(self):
        for record in self:
            if record.res_partner_id.name != False:
                record.name = record.res_partner_id.name
                # if (record.res_partner_id.district_id.name != False and record.res_partner_id.state_id.name != False):
                record.address = str(record.res_partner_id.district_id.name) + ', ' + str(record.res_partner_id.state_id.name)

class ReportAccessControl(models.Model):
    _name = 'report.access.control'
    _description = "Report Access Control"

    f_date = fields.Date('From date')
    t_date = fields.Date('To date')

    def action_print_report(self):
        # action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        # action = self.env['access.control'].search([('in_time', '>=', self.f_date), ('in_time', '<=', self.t_date)])#._for_xml_id('access_control.access_control_action_form')
        action = self.env["ir.actions.actions"]._for_xml_id('access_control.action_access')#.action_report_access_control')
        action['domain'] = [('in_time', '>=', self.f_date), ('in_time', '<=', self.t_date)]
        return action


