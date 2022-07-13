from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    payment_type = fields.Selection([('later', 'Pay later'), ('now', 'Pay now')], string="Payment_type")
