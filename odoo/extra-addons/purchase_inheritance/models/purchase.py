
from datetime import datetime


from odoo import api, fields, models, _
from odoo.osv import expression


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES, change_default=True, tracking=True,
                                 domain="[('code', 'like', 'NCC%')]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        super(PurchaseOrder, self).onchange_partner_id()
        if self.partner_id:
            self.partner_ref = self.partner_id.code

    amount_untaxed_5 = fields.Monetary(string='Price Amount', compute='_amount_price')
    @api.depends('order_line.price_total')
    def _amount_price(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = 0.0
            for line in order.order_line:
                    amount_untaxed += line.price_subtotal
            order.update({
                'amount_untaxed_5': amount_untaxed,
            })


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
            domain = expression.AND([domain, [('date_order', '>=', self.f_date)]])
        if self.t_date:
            domain = expression.AND([domain, [('date_order', '<=', self.t_date)]])
        action['domain'] = domain
        return action