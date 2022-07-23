from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    move_lines = fields.One2many('stock.move', 'picking_id', string="Stock Moves", copy=True)
    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=True, help="Date at which the transfer has been processed or cancelled.")

    @api.depends('product_id')
    def _compute_alert(self):
        '''
        This function computes the number of quality alerts generated from given picking.
        '''
        for picking in self:
            alerts = self.env['quality.alert'].search([('picking_id', '=', picking.id)])
            picking.alert_ids = alerts
            picking.alert_count = len(alerts)
        for rec in self:
            measures = self.env['quality.measure'].search([('product_id', '=', rec.product_id.id)])
            if measures:
                rec.alert_count = 1

    def quality_alert_action(self):
        '''This function returns an action that display existing quality alerts generated from a given picking.'''
        action = self.env.ref('quality_assurance.quality_alert_action')
        result = action.read()[0]

        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        alert_ids = self.env['quality.alert'].search([('stock_quant_id', '=', self.id)]).ids
        # choose the view_mode accordingly
        if len(alert_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, alert_ids)) + "])]"
        elif len(alert_ids) == 1:
            res = self.env.ref('quality_assurance.quality_alert_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = alert_ids and alert_ids[0] or False
        return result

    alert_count = fields.Integer(compute='_compute_alert', string='Quality Alerts', default=0)
    alert_ids = fields.Many2many('quality.alert', compute='_compute_alert', string='Quality Alerts', copy=False)

    def generate_quality_alert(self):
        '''
        This function generates quality alerts for the products mentioned in move_lines of given picking and also have quality measures configured.
        '''
        quality_alert = self.env['quality.alert']
        quality_measure = self.env['quality.measure']

        measures = quality_measure.search([('product_id', '=', self.product_id.id)])
        if measures:
            data = self.env['quality.alert'].search([('stock_quant_id', '=', self.id)])
            if len(data) == 0:
                quality_alert.create({
                    'name': self.env['ir.sequence'].next_by_code('quality.alert') or _('New'),
                    'product_id': self.product_id.id,
                    # 'picking_id': None,
                    'stock_quant_id': self.id,
                    'location_id': self.location_id.id,
                    'lot_id': self.lot_id.id,
                    'origin': self.lot_id.name,
                    'company_id': self.company_id.id,
                })
            self.quality_alert_action()

    def action_confirm(self):
        if self.alert_count == 0:
            self.generate_quality_alert()
        res = super(StockQuant, self).action_confirm()
        return res

    def force_assign(self):
        if self.alert_count == 0:
            self.generate_quality_alert()
        res = super(StockQuant, self).force_assign()
        return res

    def _action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        # TDE FIXME: draft -> automatically done, if waiting ?? CLEAR ME
        todo_moves = self.mapped('move_lines').filtered(
            lambda self: self.state in ['draft', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                if moves:  # could search move that needs it the most (that has some quantities left)
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                        'name': _('New Move:') + ops.product_id.display_name,
                        'product_id': ops.product_id.id,
                        'product_uom_qty': ops.qty_done,
                        'product_uom': ops.product_uom_id.id,
                        'location_id': pick.location_id.id,
                        'location_dest_id': pick.location_dest_id.id,
                        'picking_id': pick.id,
                    })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    # 'qty_done': ops.qty_done})

        for move in todo_moves:
            alerts = self.env['quality.alert'].search(
                [('picking_id', '=', self.id), ('product_id', '=', move.product_id.id)])
            for alert in alerts:
                if alert.final_status == 'wait':
                    raise UserError(_('There are items still in quality test'))
                if alert.final_status == 'fail':
                    raise UserError(_('There are items failed in quality test'))
        todo_moves._action_done()
        self.write({'date_done': fields.Datetime.now()})
        return True
