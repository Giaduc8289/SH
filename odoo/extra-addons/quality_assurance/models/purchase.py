# -*- coding: utf-8 -*-
from odoo import api, models, fields

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _create_picking(self):
        stock_picking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    res = order._prepare_picking()
                    picking = stock_picking.create(res)
                else:
                    picking = pickings[0]
                moves = order.order_line._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.generate_quality_alert()
                picking.message_post_with_view('mail.message_origin_link',
                                               values={'self': picking, 'origin': order},
                                               subtype_id=self.env.ref('mail.mt_note').id)
        return True


class QualityPurchaseReportWizard(models.TransientModel):
    _name = 'quality.purchase.report.wizard'

    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='To Date')
    sanpham = fields.Many2one("product.template", "Sản phẩm",
                              domain="[('default_code', 'not like', 'OT%'), ('categ_id', 'not in', (10, 11, 12))]")
    ketqua = fields.Selection([('pass', 'Đạt'), ('fail', 'Không đạt'), ('wait', 'Đợi')], 'Kết quả')
    nhacungcap = fields.Many2one("res.partner", "Nhà cung cấp", domain="[('code', 'like', 'NCC%')]")
    kho = fields.Many2one("stock.location", "Kho", domain="[('id', '!=', None), ('usage', '!=', 'view')]")

    def get_report(self):
        date_start = self.date_start
        date_end   = self.date_end
        domain = []
        if self.date_start:
            domain = expression.AND([domain, [('date', '>=', self.date_start)]])
            date_start = date_start.strftime('%d/%m/%Y')
        if self.date_end:
            domain = expression.AND([domain, [('date', '<=', self.date_end)]])
            date_end =date_end.strftime('%d/%m/%Y')
        if self.nhacungcap:
            domain = expression.AND([domain, [('picking_id.partner_id', '=', self.nhacungcap.id)]])
        if self.sanpham:
            domain = expression.AND([domain, [('product_id', '=', self.sanpham.id)]])
        if self.ketqua:
            domain = expression.AND([domain, [('final_status', 'like', self.ketqua)]])
        if self.kho:
            domain = expression.AND([domain, [('picking_id.location_dest_id', '=', self.kho.id)]])
        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'date_start': date_start, 'date_end': date_end, 'domain': domain, 'nhacungcap': self.nhacungcap.name, 'sanpham': self.sanpham.name,
                'kho': self.kho.complete_name, 'ketqua': self.ketqua
            },
        }

        action = self.env.ref('quality_assurance.action_report_quality_purchase').report_action(self, data=data)
        return action


class ReportQualityPurchase(models.AbstractModel):
    _name = 'report.quality_assurance.report_quality_purchase_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        domain = data['form']['domain']
        nhacungcap = data['form']['nhacungcap']
        sanpham = data['form']['sanpham']
        kho = data['form']['kho']
        ketqua = data['form']['ketqua']

        data_qa = self.env['quality.alert'].search(domain)
        docs = self.env['quality.alert'].browse(data_qa.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'nhacungcap': nhacungcap,
            'sanpham': sanpham,
            'kho': kho,
            'ketqua': ketqua,
            'docs': docs,
        }
