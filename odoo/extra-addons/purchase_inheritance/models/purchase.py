from datetime import datetime

from odoo import api, fields, models, _

from datetime import datetime, timedelta

from odoo.osv import expression

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, states=READONLY_STATES,
                                 change_default=True, tracking=True,
                                 domain="[('code', 'like', 'NCC%')]",
                                 help="You can find a vendor by its Name, TIN, Email or Internal Reference.")

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

    product_cate = ('5', '10', '11', '12')
    f_date = fields.Date('From date')
    t_date = fields.Date('To date')
    state = fields.Selection(
        [('continue', 'Hợp đồng đang thực hiện'), ('finish', 'Hợp đồng đã thực hiện'), ('cancel', 'Hợp đồng đã hủy')],
        'Hợp đồng')
    group_products = fields.Many2one("product.category", "Nhóm sản phẩm",
                                     domain="['&','&', '&' ,('id', '!=', '5') , ('id', '!=', '10'), ('id', '!=', '11'), ('id', '!=', '12')]")
    nhacungcap = fields.Many2one("res.partner", "Nhà cung cấp", domain="[('code', 'like', 'NCC%')]")
    sanpham = fields.Many2one("product.template", "Sản phẩm",
                              domain="['&','&', '&',('default_code', 'not like', 'OT%'), ('default_code', 'not like', 'BC%'),"
                                     " ('default_code', 'not like', 'BN%'), ('default_code', 'not like', 'CA%')]")

    # @api.constrains('f_date', 't_date')
    def action_print_report(self):
        action = self.env["ir.actions.actions"]._for_xml_id('purchase_inheritance.action_report_purchase_report')
        domain = []
        if self.f_date:
            domain = expression.AND([domain, [('date_order', '>=', self.f_date)]])
        if self.t_date:
            domain = expression.AND([domain, [('date_order', '<=', self.t_date)]])
        if self.state:
            if self.state == 'continue':
                trangthai = ('sent', 'draft')
            elif self.state == 'finish':
                trangthai = ('purchase',)
            else:
                trangthai = ('cancel',)
            domain = expression.AND([domain, [('state', 'in', trangthai)]])
        if self.group_products:
            domain = expression.AND([domain, [('order_line.product_id.categ_id', 'child_of', self.group_products.id)]])
        if self.nhacungcap:
            domain = expression.AND([domain, [('partner_id.code', '=', self.nhacungcap.code)]])
        action['domain'] = domain
        return action
