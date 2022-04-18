from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

class AccessControl(models.Model):
    _name = 'access.control'
    _description = "Access Control"

    res_partner_id = fields.Many2one("res.partner", "Tên khách", domain="[('code', '!=', None)]")
    number_plate = fields.Char('Biển kiểm soát')
    purpose = fields.Selection([('sale', 'Nhập hàng'), ('purchase', 'Mua hàng'), ('visit', 'Làm việc')], 'Mục đích', default='purchase')
    in_date = fields.Datetime('Thời gian vào', readonly=True, required=True, default=fields.Datetime.now)
    ordinal_number = fields.Integer('Số thứ tự')
    out_date = fields.Datetime('Thời gian ra')



