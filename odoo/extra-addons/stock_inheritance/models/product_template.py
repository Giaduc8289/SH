from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = "Product Template"

    amount_package = fields.Integer(string='Số lượng bao', compute="_amount_package")
    # inventory_quantity.compute = "_inventory_quantity"

    @api.depends("qty_available")
    def _amount_package(self):
        for record in self:
            if record.weight == 0:
                record.amount_package = 0
                continue
            record.amount_package = int(record.qty_available / record.weight)

    # @api.depends("product_id", "amount_package")
    # def _inventory_quantity(self):
    #     for record in self:
    #         record.inventory_quantity = record.amount_package * record.product_id.weight

