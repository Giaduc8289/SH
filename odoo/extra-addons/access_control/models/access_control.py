from datetime import datetime, timedelta

from docutils.nodes import field

from odoo import _, fields, models, api, exceptions
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError


class AccessControl(models.Model):
    _name = 'access.control'
    _description = "Access Control"
    _rec_name = 'res_partner_id'

    res_partner_id = fields.Many2one("res.partner", "Partner", domain="[('code', '!=', None)]")
    makh = fields.Char('Code')
    name = fields.Char('Name')
    phone = fields.Char('Phone')
    taixe = fields.Char('Driver')
    address = fields.Char('Address')
    number_plate = fields.Char('Number plate')
    purpose = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('visit', 'Visit'), ('work', 'Work')],
                               'Purpose', default='purchase')
    in_time = fields.Datetime('In time', readonly=True, required=True, default=fields.Datetime.now)
    ordinal_number = fields.Integer('Ordinal number', default=0)
    out_time = fields.Datetime('Out time')

    weight_in = fields.Float('Weight in', default=0)
    weight_out = fields.Float('Weight out', default=0)
    weight_goods = fields.Float('Weight goods', compute='_weight_goods')

    product_template_ids = fields.Many2many('product.template', column1='product_template_id', column2='id',
                                            relation='access_control_product_template_rel', string="Products")
    product_category_ids = fields.Many2many('product.category', column1='product_category_id', column2='id',
                                            relation='access_control_product_category_rel', string="Product Category",
                                            domain="[('parent_id', '=', None)]")
    purpose_descript = fields.Char('Purpose descript')

    sale_ids = fields.Many2many('sale.order', column1='sale_id', column2='id', relation='access_control_sale_order_rel',
                                string='Sale Orders')
    purchase_ids = fields.Many2many('purchase.order', column1='purchase_id', column2='id',
                                    relation='access_control_purchase_order_rel', string='Purchase Orders')

    state = fields.Selection([
        ('in', 'In'),
        ('weighin', 'Vehicle Weigh In'),
        ('unload', 'Unload Goods'),
        ('weighout', 'Vehicle Weigh Out'),
        ('out', 'Out'),
    ], string='Status', readonly=True, copy=False, index=True, default='in')

    @api.depends("weight_in", "weight_out")
    def _weight_goods(self):
        for record in self:
            record.weight_goods = abs(record.weight_in - record.weight_out)

    @api.onchange('purpose')
    def onchange_purpose(self):
        for rec in self:
            if (rec.purpose == 'purchase'):
                return {'domain': {'product_template_ids': [('categ_id', 'in', [10, 11, 12])],
                                   'res_partner_id': [('code', 'like', 'KH%')]}}
            else:
                return {'domain': {'product_template_ids': [('categ_id', 'not in', [10, 11, 12])],
                                   'res_partner_id': [('code', 'like', 'NCC%')]}}

    @api.model
    def create(self, vals_list):
        d = datetime.now()
        dt_start = d - timedelta(hours=d.hour, minutes=d.minute + 1)
        data_acs = self.env['access.control'].search(
            [('in_time', '<=', d + timedelta(days=1)), ('in_time', '>=', dt_start)])
        # if len(data) == 0:
        #     self.env.cr.execute('alter sequence access_control.access_control_id_seq restart with 1')
        if ('ordinal_number' in vals_list and vals_list['ordinal_number'] == 0) or 'ordinal_number' not in vals_list:
            # seq = self.env.ref('access_control.sequence_ordinal_number_control_access')
            vals_list['ordinal_number'] = len(data_acs) + 1  # seq.next_by_id()
        return super(AccessControl, self).create(vals_list)

    @api.model
    def update_ordinal_number(self, data):
        # seq = self.env.ref('access_control.sequence_ordinal_number_control_access')
        d = datetime.now()
        dt_start = d - timedelta(hours=d.hour, minutes=d.minute + 1)
        data_acs = self.env['access.control'].search([('in_time', '<=', d), ('in_time', '>=', dt_start)])
        temp = self.browse(data)
        temp.ordinal_number = len(data_acs) + 1  # seq.next_by_id()

    def action_weigh_in(self):
        for record in self:
            if (record.state == 'in'):
                record.state = 'weighin'

    def action_unload(self):
        for record in self:
            if (record.state == 'weighin'):
                record.state = 'unload'
            if (record.purpose == 'sale'):
                action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
            if (record.purpose == 'purchase'):
                action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        return action

    def action_purchase(self):
        action = self.env["ir.actions.actions"]
        for record in self:
            if (record.state == 'weighin'):
                record.state = 'unload'
            if ((record.state in ('weighin', 'unload')) and (record.purpose == 'sale')):
                action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        # if action is None:
        #     raise exceptions.UserError(_("No action available for this job"))
        return action

    def action_sale(self):
        action = self.env["ir.actions.actions"]
        for record in self:
            if (record.state == 'weighin'):
                record.state = 'unload'
            if ((record.state in ('weighin', 'unload')) and (record.purpose == 'purchase')):
                action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        # if action is None:
        #     raise exceptions.UserError(_("No action available for this job"))
        return action

    def action_weigh_out(self):
        for record in self:
            if (record.state == 'unload'):
                record.state = 'weighout'

    def action_check_out(self):
        for record in self:
            if (record.state != 'out'):
                record.out_time = fields.Datetime.now()
                record.state = 'out'

    @api.onchange('res_partner_id')
    def _compute_inf_partner(self):
        for record in self:
            if record.res_partner_id.name != False:
                record.name = record.res_partner_id.name
            record.makh = record.res_partner_id.code
            # if (record.res_partner_id.district_id.name != False and record.res_partner_id.state_id.name != False):
            if record.res_partner_id.street != False:
                record.address = str(record.res_partner_id.street) + ' '
            if record.res_partner_id.village_id.name != False:
                record.address = record.address + str(record.res_partner_id.village_id.name) + ', '
            if record.res_partner_id.district_id.name != False:
                record.address = record.address + str(record.res_partner_id.district_id.name) + ', '
            if record.res_partner_id.state_id.name != False:
                record.address = record.address + str(record.res_partner_id.state_id.name)
            record.phone = record.res_partner_id.phone


# def action_print_report(self):
#     action = self.env.ref('access_control.action_report_access_control').report_action(None, data=None)
#     return action


class FilterAccessControl(models.Model):
    _name = 'filter.access.control'
    _rec_name = 'f_date'

    f_date = fields.Date('From date')
    t_date = fields.Date('To date')
    purpose = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('visit', 'Visit'), ('work', 'Work')],
                               'Purpose')
    res_partner_id = fields.Many2one("res.partner", "Partner", domain="[('code', '!=', None)]")

    def action_print_report_access_control(self):
        # action = self.env["ir.actions.actions"]._for_xml_id('access_control.action_filter_access_control')
        domain = []
        if self.f_date:
            domain = expression.AND([domain, [('in_time', '>=', self.f_date)]])
        if self.t_date:
            domain = expression.AND([domain, [('in_time', '<=', self.t_date)]])
        if self.purpose:
            domain = expression.AND([domain, [('purpose', '=', self.purpose)]])
        if self.res_partner_id:
            domain = expression.AND([domain, [('res_partner_id.code', 'like', self.res_partner_id.code)]])
        # action['domain'] = domain
        datas = self.env['access.control'].search(domain)
        docs = self.env['access.control'].browse(datas.ids)
        # data = {'date_start': self.start_date, 'date_stop': self.end_date, 'config_ids': self.pos_config_ids.ids}
        action = self.env.ref('access_control.action_report_access_control').report_action(docs)
        return action

    def action_print_report_weight(self):
        # action = self.env["ir.actions.actions"]._for_xml_id('access_control.action_filter_access_control')
        domain = []
        if self.f_date:
            domain = expression.AND([domain, [('in_time', '>=', self.f_date)]])
        if self.t_date:
            domain = expression.AND([domain, [('in_time', '<=', self.t_date)]])
        if self.purpose:
            domain = expression.AND([domain, [('purpose', '=', self.purpose)]])
        if self.res_partner_id:
            domain = expression.AND([domain, [('res_partner_id.code', 'like', self.res_partner_id.code)]])
        # action['domain'] = domain
        datas = self.env['access.control'].search(domain)
        docs = self.env['access.control'].browse(datas.ids)
        action = self.env.ref('access_control.action_report_weight_vehicle').report_action(docs)
        return action


# class AccessControlReport(models.AbstractModel):
#     _name = 'access.control.report_access_control_document'
#
#     @api.model
#     def _get_report_values(self, docids, data):
#         docs = self.env['access.control'].browse(data.ids)
#         return {
#             'doc_ids': docids,
#             'doc_model': 'access.control',
#             'docs': docs,
#             'data': data,
#         }
