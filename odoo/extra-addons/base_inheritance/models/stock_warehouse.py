from odoo import models, fields


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    phone_number = fields.Char(related='partner_id.phone', readonly=True, string="Phone number")
