# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    group_products = fields.Many2one("product.category", "Nhóm sản phẩm", domain="[('id', '!=', None)]")
    vung = fields.Many2one("res.country.state", "Tỉnh/ Thành phố", domain="[('code', 'like', 'VN-%')]")
    khachhang = fields.Many2one("res.partner", "Khách hàng", domain="[('code', 'like', 'KH%')]")
    sanpham = fields.Many2one("product.template", "Sản phẩm", domain="[('default_code', 'not like', 'OT%')]")
    nhanvienkinhdoanh = fields.Many2one("res.partner", "Nhân viên kinh doanh", domain="[('user_id', '=', None)]")

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
        if self.group_products:
            domain = expression.AND([domain, [('order_line.product_id.categ_id', 'child_of', self.group_products.id)]])
        if self.vung:
            domain = expression.AND([domain, [('partner_id.state_id', '=', self.vung.name)]])
        if self.khachhang:
            domain = expression.AND([domain, [('partner_id.code', '=', self.khachhang.code)]])
        if self.sanpham:
            domain = expression.AND([domain, [('order_line.product_id', '=', self.sanpham.id)]])
        if self.nhanvienkinhdoanh:
            domain = expression.AND([domain, [('partner_id.user_id.name', '=', self.nhanvienkinhdoanh.name)]])

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': date_start, 'date_end': date_end, 'group_products': self.group_products.complete_name, 'vung': self.vung.name, 'khachhang':self.khachhang.name, 'sanpham':self.sanpham.name,
                'nhanvienkinhdoanh':self.nhanvienkinhdoanh.name, 'domain': domain
            },
        }

        action = self.env.ref('sale_inheritance.action_report_sale_order_bc').report_action(self, data=data)
        return action

class ReportSale(models.AbstractModel):
    _name = 'report.sale_inheritance.report_sale_order_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        group_products = data['form']['group_products']
        vung = data['form']['vung']
        khachhang = data['form']['khachhang']
        sanpham = data['form']['sanpham']
        nhanvienkinhdoanh = data['form']['nhanvienkinhdoanh']
        domain = data['form']['domain']

        data_sa = self.env['sale.order'].search(domain)
        docs = self.env['sale.order'].browse(data_sa.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'group_products': group_products,
            'vung': vung,
            'khachhang': khachhang,
            'sanpham': sanpham,
            'nhanvienkinhdoanh': nhanvienkinhdoanh,
            'docs': docs,
        }

