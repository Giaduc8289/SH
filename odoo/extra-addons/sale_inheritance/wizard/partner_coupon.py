from operator import itemgetter

from odoo import models, fields, api

from datetime import datetime, timedelta

from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, groupby
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

class PartnerCouponWizard(models.TransientModel):
    _name = 'partner.coupon.wizard'
    _rec_name = 'khachhang'

    khachhang = fields.Many2one("res.partner", "Khách hàng", domain="[('code', 'like', 'KH%')]", required=True)
    name_coupon = fields.Many2one("coupon.program", "Tên chương trình", readonly=True, store=True)
    product_coupon = fields.Many2one("product.template", "Tên sản phẩm", readonly=True, store=True)
    fixed_price = fields.Many2one("product.pricelist.item", "Giá sản phẩm", readonly=True, store=True)
    discount_percentage = fields.Many2one("coupon.reward", "Phần trăm giảm", readonly=True, store=True)
    discount_hold_time = fields.Many2one("coupon.reward", "Thời gian hoàn tiền", readonly=True, store=True)
    payment_type = fields.Many2one("coupon.program", "Kiểu thanh toán", readonly=True, store=True)
    discount_type = fields.Many2one("coupon.reward", "Kiểu chương trình", readonly=True, store=True)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.", store=True)
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True, ondelete="restrict")
    # amount_coupon = fields.Monetary(string='Price Amount', compute='_amount_coupon_price')
    #
    # def _amount_coupon_price(self):
    #     coupon_price = 0.0
    #     for record in self:
    #         if(record.discount_type == 'percentage'):
    #             coupon_price = record.fixed_price - (record.fixed_price * record.discount_percentage / 100)
    #         record.update({
    #             'amount_coupon': coupon_price,
    #         })

    def get_report(self):
        code = self.khachhang.code

        query = """
        SELECT cp.name as name_coupon,  product_template.name as product_coupon, fixed_price
            from coupon_program cp join coupon_program_product_template_rel cp_pt_rel on cp.id = cp_pt_rel.coupon_program_id
            join coupon_program_res_partner_rel on cp.id = coupon_program_res_partner_rel.coupon_program_id
            join product_pricelist_item on cp_pt_rel.id = product_pricelist_item.product_tmpl_id
            join res_partner ON res_partner.id = coupon_program_res_partner_rel.code
            join coupon_reward on coupon_reward.id = cp.reward_id
            join product_template on product_template.id = cp_pt_rel.id
            where res_partner.code=%s
        """

        self.env.cr.execute(query, (code,))
        data_sa = self.env.cr.fetchall()
        # tính toán ra 1 data_wizard
        # danh sách sản phẩm ở trong data_sa
        # values = set(map(lambda x: x[1], data_sa))
        # data_sp = [[y[0] for y in data_sa if y[1] == x] for x in values]
        data_sa.sort(key=itemgetter(1))
        data_sp = groupby(data_sa, itemgetter(1))
        # data_sp = data_sa.read_group(fields=['product_coupon'], groupby=['product_coupon'])
        data_final = []
        # for sp in data_sp:
        #     #tao moi dong du lieu cho san pham
        #     data_row=[]
        #     data_row.append({'product_coupon': sp[0]})
        #     for ct in sp[1]:
        #         data_row.append({
        #             ct[0]: ct[2],
        #         })
        #     data_final.append(data_row)
        for sp in data_sp:
            #tao moi dong du lieu cho san pham
            for ct in sp[1]:
                data_row = ({
                    'product_coupon': sp[0],
                    'name_coupon': ct[0],
                    'fixed_price': ct[2],
                })
                data_final.append(data_row)

        docs = self.env['partner.coupon.wizard'].browse(data_final)

        data = {
            'model': self._name,
            'form': {
                'khachhang': self.khachhang.name,
                'code': code,
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

        query = """
            SELECT cp.name as name_coupon,  product_template.name as product_coupon, fixed_price, discount_percentage, discount_hold_time, payment_type, discount_type 
            from coupon_program cp join coupon_program_product_template_rel cp_pt_rel on cp.id = cp_pt_rel.coupon_program_id 
            join coupon_program_res_partner_rel on cp.id = coupon_program_res_partner_rel.coupon_program_id 
            join product_pricelist_item on cp_pt_rel.id = product_pricelist_item.product_tmpl_id 
            join res_partner ON res_partner.id = coupon_program_res_partner_rel.code 
            join coupon_reward on coupon_reward.id = cp.reward_id 
            join product_template on product_template.id = cp_pt_rel.id 
            where res_partner.code=%s 
        """
        self.env.cr.execute(query, (code,))
        data_sa = self.env.cr.fetchall()
        # tính toán ra 1 data_wizard
        # danh sách sản phẩm ở trong data_sa
        data_sa.sort(key=itemgetter(1))
        data_sp = groupby(data_sa, itemgetter(1))
        data_final = []
        for sp in data_sp:
            for ct in sp[1]:
                data_row = ({
                    'product_coupon': sp[0],
                    'name_coupon': ct[0],
                    'fixed_price': ct[2],
                })
                data_final.append(data_row)

        docs = self.env['partner.coupon.wizard'].browse(data_final)

        return {
            # 'doc_ids': data['ids'],
            'doc_model': 'partner.coupon.wizard',
            'khachhang': khachhang,
            'docs': docs,
        }

