
from datetime import datetime


from odoo import api, fields, models, _


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
        if self.f_date == False:
            self.f_date = datetime.strptime('01/01/1900', '%d/%m/%Y')
        if self.t_date == False:
            self.t_date = datetime.strptime('31/12/9999', '%d/%m/%Y')
        action['domain'] = [('date_order', '>=', self.f_date), ('date_order', '<=', self.t_date)]
        return action