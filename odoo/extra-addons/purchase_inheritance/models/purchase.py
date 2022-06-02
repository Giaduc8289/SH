
from datetime import datetime


from odoo import api, fields, models, _
from odoo.osv import expression


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id:
            self.partner_ref = self.partner_id.code

class FilterPurchaseOrder(models.Model):
    _name = 'filter.purchase.order'
    _rec_name = 't_date'

    f_date = fields.Date('From date')
    t_date = fields.Date('To date')

    # @api.constrains('f_date', 't_date')
    def action_print_report(self):
        action = self.env["ir.actions.actions"]._for_xml_id('purchase_inheritance.action_purchase_order_1')
        domain = []
        if self.f_date:
            domain = expression.AND([domain, [('in_time', '>=', self.f_date)]])
        if self.t_date:
            domain = expression.AND([domain, [('in_time', '<=', self.t_date)]])
        action['domain'] = domain
        return action