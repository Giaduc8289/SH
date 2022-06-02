from datetime import datetime, timedelta

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import ValidationError
from odoo.osv import expression


class StockMoveInventory(models.Model):
    _name = 'stock.move.inventory'
    _description = 'Stock Move Inventory'

    # location_id = fields.Many2one(
    #     'stock.location', 'Location',
    #     domain=lambda self: [('name', '=', 'Kho')],#self._domain_location_id(),
    #     auto_join=True, ondelete='restrict', required=True, index=True, check_company=True)
    # product_id = fields.Many2one('product.product', 'Product')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    begin_inventory = fields.Float('Beginning Inventory')
    warehouse_entry = fields.Float('Warehouse Entry')
    warehouse_export = fields.Float('Warehouse Export')
    end_inventory = fields.Float('End Inventory')

    def action_print_report(self):
        action = self.env.ref('stock_inheritance.action_report_stock_move_inventory').report_action(None, data=None)
        return action

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
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')

    def action_filter_data(self):
        tree_view_id = self.env.ref('stock_inheritance.stock_move_inventory_tree_view').id
        domain = [('type', '=', 'product'), ('qty_available', '>', 0)]  # , ('location_id', '=', self.location_id)]
        if self.product_tmpl_id:
            domain = expression.AND([domain, [('product_tmpl_id', '=', self.product_tmpl_id)]])
        # We pass `to_date` in the context so that `qty_available` will be computed across
        # moves until date.
        begin_inventory_data = self.env['product.product'].search(domain).with_context(self.env.context,
                                                                                       to_date=self.f_date)
        end_inventory_data = self.env['product.product'].search(domain).with_context(self.env.context,
                                                                                     to_date=self.t_date + timedelta(
                                                                                         days=1))
        self.env.cr.execute("delete from stock_move_inventory")
        self.env['stock.move.inventory'].create([{
            'product_tmpl_id': record.id,
            'begin_inventory': record.qty_available,
            'warehouse_entry': 0,
            'warehouse_export': 0,
            'end_inventory': 0,
        } for record in begin_inventory_data])
        self.env['stock.move.inventory'].create([{
            'product_tmpl_id': record.id,
            'begin_inventory': 0,
            'warehouse_entry': 0,
            'warehouse_export': 0,
            'end_inventory': record.qty_available,
        } for record in end_inventory_data])

        location_internal = self.env['stock.location'].search([('usage', 'in', ['internal'])])
        entry_data = self.env['stock.move'].search(
            [('location_id', 'not in', location_internal.ids), ('location_dest_id', 'in', location_internal.ids),
             ('state', '=', 'done'), ('product_qty', '>', 0)])
        export_data = self.env['stock.move'].search(
            [('location_id', 'in', location_internal.ids), ('location_dest_id', 'not in', location_internal.ids),
             ('state', '=', 'done'), ('product_qty', '>', 0)])
        self.env['stock.move.inventory'].create([{
            'product_tmpl_id': record.product_id.id,
            'begin_inventory': 0,
            'warehouse_entry': record.product_qty,
            'warehouse_export': 0,
            'end_inventory': 0,
        } for record in entry_data])
        self.env['stock.move.inventory'].create([{
            'product_tmpl_id': record.product_id.id,
            'begin_inventory': 0,
            'warehouse_entry': 0,
            'warehouse_export': record.product_qty,
            'end_inventory': 0,
        } for record in export_data])

        sql_command = '''
        select product_tmpl_id, sum(begin_inventory) as begin_inventory
            , sum(warehouse_entry) as warehouse_entry
            , sum(warehouse_export) as warehouse_export
            , sum(end_inventory) as end_inventory
        from stock_move_inventory
        group by product_tmpl_id
        '''
        self.env.cr.execute(sql_command)
        records = self.env.cr.fetchall()
        self.env.cr.execute("delete from stock_move_inventory")
        # for record in records:
        #     self.env['stock.move.inventory'].append(record)
        self.env['stock.move.inventory'].create([{
            'product_tmpl_id': record[0],
            'begin_inventory': record[1],
            'warehouse_entry': record[2],
            'warehouse_export': record[3],
            'end_inventory': record[4],
        } for record in records])

        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'name': _('Products'),
            'res_model': 'stock.move.inventory',
            # 'domain': domain,
            # 'context': dict(self.env.context, to_date=self.f_date),
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
