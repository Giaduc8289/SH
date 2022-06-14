# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ReportAccessControl(models.Model):
    _name = 'report.access.control'
    _auto = False
    _description = 'Access Control Report'

    f_date = fields.Date('From date')
    t_date = fields.Date('To date')
    purpose = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('visit', 'Visit'), ('work', 'Work')],
                               'Purpose')
    res_partner_id = fields.Many2one("res.partner", "Partner", domain="[('code', '!=', None)]")

    name = fields.Char('Name')
    address = fields.Char('Address')
    number_plate = fields.Char('Number plate')
    in_time = fields.Datetime('In time', readonly=True, required=True, default=fields.Datetime.now)
    ordinal_number = fields.Integer('Ordinal number', default=0)
    out_time = fields.Datetime('Out time')

    weight_in = fields.Float('Weight in', default=0)
    weight_out = fields.Float('Weight out', default=0)

    purpose_descript = fields.Char('Purpose descript')

    # date = fields.Date(string='Date', readonly=True)
    # product_tmpl_id = fields.Many2one('product.template', readonly=True)
    # product_id = fields.Many2one('product.product', string='Product', readonly=True)
    # state = fields.Selection([
    #     ('forecast', 'Forecasted Stock'),
    #     ('in', 'Forecasted Receipts'),
    #     ('out', 'Forecasted Deliveries'),
    # ], string='State', readonly=True)
    # product_qty = fields.Float(string='Quantity', readonly=True)
    # move_ids = fields.One2many('stock.move', readonly=True)
    # company_id = fields.Many2one('res.company', readonly=True)
    # warehouse_id = fields.Many2one('stock.warehouse', readonly=True)

#     def init(self):
#         tools.drop_view_if_exists(self._cr, 'report_access_control')
#         query = """
# CREATE or REPLACE VIEW report_access_control AS (
# SELECT
#     res_partner_id, name, address, phone, number_plate
#     , purpose, in_time, out_time, weight_in, weight_out, state
# FROM access_control ac
# """
#         self.env.cr.execute(query)
