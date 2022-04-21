from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

class AccessControl(models.Model):
    _name = 'access.control'
    _description = "Access Control"
    _rec_name = 'res_partner_id'

    res_partner_id = fields.Many2one("res.partner", "Tên khách", domain="[('code', '!=', None)]")
    number_plate = fields.Char('Biển kiểm soát')
    purpose = fields.Selection([('sale', 'Nhập hàng'), ('purchase', 'Mua hàng'), ('visit', 'Làm việc')], 'Mục đích', default='purchase')
    in_date = fields.Datetime('Thời gian vào', readonly=True, required=True, default=fields.Datetime.now)
    ordinal_number = fields.Integer('Số thứ tự', default=0)
    out_date = fields.Datetime('Thời gian ra')

    state = fields.Selection([
        ('in', 'In'),
        ('weighin', 'Vehicle Weigh In'),
        ('unload', 'Unload Goods'),
        ('weighout', 'Vehicle Weigh Out'),
        ('out', 'Out'),
        ], string='Status', readonly=True, copy=False, index=True, default='in')

    @api.model
    def create(self, vals_list):
        if ('ordinal_number' in vals_list and vals_list['ordinal_number'] == 0) or 'ordinal_number' not in vals_list:
            seq = self.env.ref('access_control.sequence_ordinal_number_control_access')
            vals_list['ordinal_number'] = seq.next_by_id()
        return super(AccessControl, self).create(vals_list)

    @api.model
    def update_ordinal_number(self, data):
        seq = self.env.ref('access_control.sequence_ordinal_number_control_access')
        temp = self.browse(data)
        temp.ordinal_number = seq.next_by_id()

    def check_out(self):
        for record in self:
            if(record.state != 'out'):
                record.out_date = fields.Datetime.now()
                record.state = 'out'


