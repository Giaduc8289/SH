# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class PurchaseReportWizard(models.TransientModel):
    _name = 'purchase.report.wizard'
    _rec_name = 'date_start'

    product_cate = ('5', '10', '11', '12')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    state = fields.Selection(
        [('continue', 'Hợp đồng đang thực hiện'), ('finish', 'Hợp đồng đã thực hiện'), ('cancel', 'Hợp đồng đã hủy')],
        'Hợp đồng')
    group_products = fields.Many2one("product.category", "Nhóm sản phẩm",
                                     domain="['&','&', '&' ,('id', '!=', '5') , ('id', '!=', '10'), ('id', '!=', '11'), ('id', '!=', '12')]")
    nhacungcap = fields.Many2one("res.partner", "Nhà cung cấp", domain="[('code', 'like', 'NCC%')]")
    sanpham = fields.Many2one("product.template", "Sản phẩm",
                              domain="['&','&', '&',('default_code', 'not like', 'OT%'), ('default_code', 'not like', 'BC%'),"
                                     " ('default_code', 'not like', 'BN%'), ('default_code', 'not like', 'CA%')]")

    def get_report(self):
        date_start = self.date_start
        date_end = self.date_end
        domain = []
        if self.date_start:
            domain = expression.AND([domain, [('date_order', '>=', self.date_start)]])
            date_start = date_start.strftime('%d/%m/%Y')
        if self.date_end:
            domain = expression.AND([domain, [('date_order', '<=', self.date_end)]])
            date_end = date_end.strftime('%d/%m/%Y')

        # if self.invoice_status:
        #     domain = expression.AND([domain, [('invoice_status', '=', self.invoice_status)]])
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
            domain = expression.AND([domain, [('partner_id', '=', self.nhacungcap.id)]])
        if self.sanpham:
            domain = expression.AND([domain, [('order_line.product_id', '=', self.sanpham.id)]])

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': date_start, 'date_end': date_end, 'group_products': self.group_products.complete_name, 'state': self.state, 'nhacungcap': self.nhacungcap.name,
                'sanpham': self.sanpham.name, 'domain': domain
            },
        }

        action = self.env.ref('purchase_inheritance.action_report_purchase_order').report_action(self, data=data)
        return action

class ReportPurchase(models.AbstractModel):
    _name = 'report.purchase_inheritance.report_purchase_order_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        group_products = data['form']['group_products']
        state = data['form']['state']
        sanpham = data['form']['sanpham']
        nhacungcap = data['form']['nhacungcap']
        domain = data['form']['domain']
        data_pu = self.env['purchase.order'].search(domain)
        docs = self.env['purchase.order'].browse(data_pu.ids)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'group_products': group_products,
            'state': state,
            'nhacungcap': nhacungcap,
            'sanpham': sanpham,
            'docs': docs,
        }

