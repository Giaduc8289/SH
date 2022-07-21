from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class PartnerCouponWizard(models.TransientModel):
    _name = 'partner.coupon.wizard'
    _rec_name = 'khachhang'

    khachhang = fields.Many2one("res.partner", "Khách hàng", domain="[('code', 'like', 'KH%')]", required=True)

    def get_report(self):
        code = self.khachhang.code

        query = "SELECT * " \
                "from coupon_program " \
                "join coupon_program_product_template_rel on coupon_program.id = coupon_program_product_template_rel.coupon_program_id " \
                "join coupon_program_res_partner_rel on coupon_program.id = coupon_program_res_partner_rel.coupon_program_id " \
                "join product_pricelist_item on coupon_program_product_template_rel.id = product_pricelist_item.product_tmpl_id " \
                "join res_partner ON res_partner.id = coupon_program_res_partner_rel.code " \
                "join coupon_reward on coupon_reward.id = coupon_program.reward_id " \
                "where res_partner.code=%s"
        self.env.cr.execute(query, (code,))
        data_sa = self.env.cr.fetchall()
        docs = self.env['coupon.program'].browse(data_sa.ids)

        data = {
            'model': self._name,
            'ids': self.ids,
            'form': {
                'khachhang': self.khachhang.name,  'code': code
            },
        }
        action = self.env.ref('sale_inheritance.action_report_discount_coupon').report_action(self, data=data)
        return action

class DiscountCouponReport(models.AbstractModel):
    _name = 'report.sale_inheritance.report_discount_coupon_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        khachhang = data['form']['khachhang']
        code = data['form']['code']

        query = "SELECT * " \
                "from coupon_program " \
                "join coupon_program_product_template_rel on coupon_program.id = coupon_program_product_template_rel.coupon_program_id " \
                "join coupon_program_res_partner_rel on coupon_program.id = coupon_program_res_partner_rel.coupon_program_id " \
                "join product_pricelist_item on coupon_program_product_template_rel.id = product_pricelist_item.product_tmpl_id " \
                "join res_partner ON res_partner.id = coupon_program_res_partner_rel.code " \
                "join coupon_reward on coupon_reward.id = coupon_program.reward_id " \
                "where res_partner.code=%s"
        self.env.cr.execute(query, (code,))
        data_sa = self.env.cr.fetchall()
        docs = self.env['coupon.program'].browse(data_sa.ids)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'khachhang': khachhang,
            # 'code': code,
            'docs': docs,
        }
