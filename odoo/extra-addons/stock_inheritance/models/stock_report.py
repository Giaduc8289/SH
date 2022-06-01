from datetime import datetime

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError
from odoo.osv import expression

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    _description = "Stock Quant"

    def action_print_report(self):
        action = self.env.ref('stock_inheritance.action_report_stock_move_inventory').report_action(None, data=None)
        return action

class StockMoveInventory(models.Model):
    _name = 'stock.move.inventory'
    _description = 'Stock Move Inventory'

    location_id = fields.Many2one(
        'stock.location', 'Location',
        domain=lambda self: [('name', '=', 'Kho')],#self._domain_location_id(),
        auto_join=True, ondelete='restrict', required=True, index=True, check_company=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    begin_inventory = fields.Float('Beginning Inventory')
    warehouse_entry = fields.Float('Warehouse Entry')
    warehouse_export = fields.Float('Warehouse Export')
    end_inventory = fields.Float('End Inventory')

class FilterStockQuant(models.Model):
    _name = 'filter.stock.quant'
    _rec_name = 'f_date'

    @api.model
    def _is_inventory_mode(self):
        return self.env.context.get('inventory_mode') and self.user_has_groups('stock.group_stock_user')

    def _domain_location_id(self):
        if not self._is_inventory_mode():
            return
        return [('usage', 'in', ['internal', 'transit'])]

    f_date = fields.Date('From date', default=datetime.now().date())
    t_date = fields.Date('To date', default=datetime.now().date())
    # product_id = fields.Many2one('product.product', 'Product')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    location_id = fields.Many2one(
        'stock.location', 'Location',
        domain=lambda self: [('name', '=', 'Kho')],#self._domain_location_id(),
        auto_join=True, ondelete='restrict', required=True, index=True, check_company=True)

    def action_filter_data(self):
        tree_view_id = self.env.ref('stock.view_stock_product_tree').id
        domain = [('type', '=', 'product'), ('qty_available', '>', 0)]
        if self.product_tmpl_id:
            domain = expression.AND([domain, [('product_tmpl_id', '=', self.product_tmpl_id)]])
        # We pass `to_date` in the context so that `qty_available` will be computed across
        # moves until date.
        begin_inventory_data = self.env['product.product'].search(domain).with_context(self.env.context, to_date=self.f_date)
        end_inventory_data = self.env['product.product'].search(domain).with_context(self.env.context, to_date=self.t_date.day.__add__(1) )
        inventory_data = self.env['stock.move.inventory'].clear_caches()
        for record in begin_inventory_data:
            reward_dict = {}
            reward_dict[record.product_tmpl_id] = {
                'begin_inventory': record.qty_available,
                'warehouse_entry': 0,
                'warehouse_export': 0,
                'end_inventory': 0,
            }
            inventory_data.add(reward_dict)
        for record in end_inventory_data:
            reward_dict = {}
            reward_dict[record.product_tmpl_id] = {
                'begin_inventory': 0,
                'warehouse_entry': 0,
                'warehouse_export': 0,
                'end_inventory': record.qty_available,
            }
            inventory_data.add_data(reward_dict)

        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'name': _('Products'),
            'res_model': 'product.product',
            'domain': domain,
            'context': dict(self.env.context, to_date=self.f_date),
        }
        return action

    def open_at_date(self):
        tree_view_id = self.env.ref('stock.view_stock_product_tree').id
        form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
        domain = [('type', '=', 'product')]
        product_id = self.env.context.get('product_id', False)
        product_tmpl_id = self.env.context.get('product_tmpl_id', False)
        if product_id:
            domain = expression.AND([domain, [('id', '=', product_id)]])
        elif product_tmpl_id:
            domain = expression.AND([domain, [('product_tmpl_id', '=', product_tmpl_id)]])
        # We pass `to_date` in the context so that `qty_available` will be computed across
        # moves until date.
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Products'),
            'res_model': 'product.product',
            'domain': domain,
            'context': dict(self.env.context, to_date=self.inventory_datetime),
        }
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

