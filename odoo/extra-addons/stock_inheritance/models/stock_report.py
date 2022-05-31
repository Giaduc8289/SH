from datetime import datetime

from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    _description = "Stock Quant"

    location_dest_id = fields.Many2one('stock.move', 'Location Move', auto_join=True, ondelete='restrict', required=True, index=True, check_company=True)
    
    def action_print_report(self):
        action = self.env.ref('stock_inheritance.action_report_stock_move_inventory').report_action(None, data=None)
        return action

class FilterStockQuant(models.Model):
    _name = 'filter.stock.quant'
    _rec_name = 'f_date'

    @api.model
    def _is_inventory_mode(self):
        """ Used to control whether a quant was written on or created during an
        "inventory session", meaning a mode where we need to create the stock.move
        record necessary to be consistent with the `inventory_quantity` field.
        """
        return self.env.context.get('inventory_mode') and self.user_has_groups('stock.group_stock_user')

    def _domain_location_id(self):
        if not self._is_inventory_mode():
            return
        return [('usage', 'in', ['internal', 'transit'])]

    f_date = fields.Date('From date', default=datetime.now().date())
    t_date = fields.Date('To date', default=datetime.now().date())
    location_id = fields.Many2one(
        'stock.location', 'Location',
        domain=lambda self: self._domain_location_id(),
        auto_join=True, ondelete='restrict', required=True, index=True, check_company=True)

    def action_filter_data(self):
        action = self.env["ir.actions.actions"]._for_xml_id('stock_inheritance.action_filter_stock_move_inventory')
        if self.f_date == False:
            self.f_date = datetime.strptime('01/01/1900', '%d/%m/%Y')
        if self.t_date == False:
            self.t_date = datetime.strptime('31/12/9999', '%d/%m/%Y')
        dieukien = [self.location_id.complete_name]
        if self.location_id == False:
            dieukien = ['TP/Kho', 'BB/Kho']
        action['domain'] = [('in_date', '>=', self.f_date), ('in_date', '<=', self.t_date), ('location_id', 'in', dieukien)]
        return action

class StockQuantReport(models.AbstractModel):
    _name = 'stock.quant.report_stock_move_inventory_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.quant'].browse(docids)
        return {
              'doc_ids': docids,
              'doc_model': 'stock.quant',
              'docs': docs,
              'data': data,
        }

