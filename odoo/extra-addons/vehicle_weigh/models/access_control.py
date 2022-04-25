from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

class AccessControl(models.Model):
    _inherit = 'access.control'
    _description = "Access Control"

    weight_in = fields.Float('Weight in', default=0)
    weight_out = fields.Float('Weight out', default=0)

    state = fields.Selection(selection_add=[
        ('weighin', 'Vehicle Weigh In'),
        ('unload', 'Unload Goods'),
        ('weighout', 'Vehicle Weigh Out')])

    def check_out(self):
        for record in self:
            if(record.state != 'out'):
                record.out_date = fields.Datetime.now()
                record.state = 'out'


