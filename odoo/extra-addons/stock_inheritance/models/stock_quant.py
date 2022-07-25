from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_compare, OrderedSet, float_round, float_is_zero


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    _description = "Stock Quant"

    amount_package = fields.Integer(string='Số lượng bao', compute="_amount_package")
    # inventory_quantity.compute = "_inventory_quantity"
    manufacturing_date = fields.Datetime('Ngày sản xuất', readonly=True, default=fields.Datetime.now)
# .Many2one('stock.move.line', 'Ngày sản xuất', auto_join=True, ondelete='restrict',
#                                          index=True,
#                                          help="Select manufacturing date of stock move line for the current product")
    expiration_date = fields.Datetime('Ngày hết hạn', readonly=True, default=fields.Datetime.now)
# Many2one('stock.move.line', 'Ngày hết hạn', auto_join=True, ondelete='restrict',
#                                       index=True,
#                                       help="Select expiration date of stock move line for the current product")

    @api.depends("inventory_quantity")
    def _amount_package(self):
        for record in self:
            if record.product_tmpl_id.weight == 0:
                record.amount_package = 0
                continue
            record.amount_package = int(record.inventory_quantity / record.product_tmpl_id.weight)

            @api.model
            def _get_removal_strategy(product_id, location_id):
                if product_id.categ_id.removal_strategy_id:
                    return product_id.categ_id.removal_strategy_id.method
                loc = location_id
                while loc:
                    if loc.removal_strategy_id:
                        return loc.removal_strategy_id.method
                    loc = loc.location_id
                return 'fifo'

            @api.model
            def _get_removal_strategy_order(removal_strategy):
                if removal_strategy == 'fifo':
                    return 'in_date ASC, id'
                elif removal_strategy == 'lifo':
                    return 'in_date DESC, id DESC'
                elif removal_strategy == 'closest':
                    return 'location_id ASC, id DESC'
                raise UserError(_('Removal strategy %s not implemented.') % (removal_strategy,))

    def _gather(self, product_id, location_id, lot_id=None, manufacturing_date=None, expiration_date=None,
                package_id=None, owner_id=None, strict=False):
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = self._get_removal_strategy_order(removal_strategy)

        domain = [('product_id', '=', product_id.id)]
        if not strict:
            if lot_id:
                domain = expression.AND([[('lot_id', '=', lot_id.id)], domain])
            if manufacturing_date:
                domain = expression.AND([[('manufacturing_date', '=', manufacturing_date)], domain])
            if expiration_date:
                domain = expression.AND([[('expiration_date', '=', expiration_date)], domain])
            if package_id:
                domain = expression.AND([[('package_id', '=', package_id.id)], domain])
            if owner_id:
                domain = expression.AND([[('owner_id', '=', owner_id.id)], domain])
            domain = expression.AND([[('location_id', 'child_of', location_id.id)], domain])
        else:
            domain = expression.AND([[('lot_id', '=', lot_id and lot_id.id or False)], domain])
            domain = expression.AND([[('manufacturing_date', '=', manufacturing_date)], domain])
            domain = expression.AND([[('expiration_date', '=', expiration_date)], domain])
            domain = expression.AND([[('package_id', '=', package_id and package_id.id or False)], domain])
            domain = expression.AND([[('owner_id', '=', owner_id and owner_id.id or False)], domain])
            domain = expression.AND([[('location_id', '=', location_id.id)], domain])

        return self.search(domain, order=removal_strategy_order)

    @api.model
    def _get_available_quantity(self, product_id, location_id, lot_id=None, manufacturing_date=None,
                                expiration_date=None, package_id=None, owner_id=None, strict=False,
                                allow_negative=False):
        """ Return the available quantity, i.e. the sum of `quantity` minus the sum of
        `reserved_quantity`, for the set of quants sharing the combination of `product_id,
        location_id` if `strict` is set to False or sharing the *exact same characteristics*
        otherwise.
        This method is called in the following usecases:
            - when a stock move checks its availability
            - when a stock move actually assign
            - when editing a move line, to check if the new value is forced or not
            - when validating a move line with some forced values and have to potentially unlink an
              equivalent move line in another picking
        In the two first usecases, `strict` should be set to `False`, as we don't know what exact
        quants we'll reserve, and the characteristics are meaningless in this context.
        In the last ones, `strict` should be set to `True`, as we work on a specific set of
        characteristics.

        :return: available quantity as a float
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, manufacturing_date=manufacturing_date,
                              expiration_date=expiration_date, package_id=package_id, owner_id=owner_id, strict=strict)
        rounding = product_id.uom_id.rounding
        if product_id.tracking == 'none':
            available_quantity = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
            if allow_negative:
                return available_quantity
            else:
                return available_quantity if float_compare(available_quantity, 0.0,
                                                           precision_rounding=rounding) >= 0.0 else 0.0
        else:
            availaible_quantities = {lot_id: 0.0 for lot_id in list(set(quants.mapped('lot_id'))) + ['untracked']}
            for quant in quants:
                if not quant.lot_id:
                    availaible_quantities['untracked'] += quant.quantity - quant.reserved_quantity
                else:
                    availaible_quantities[quant.lot_id] += quant.quantity - quant.reserved_quantity
            if allow_negative:
                return sum(availaible_quantities.values())
            else:
                return sum([available_quantity for available_quantity in availaible_quantities.values() if
                            float_compare(available_quantity, 0, precision_rounding=rounding) > 0])

    @api.model
    def _update_available_quantity(self, product_id, location_id, quantity, lot_id=None, manufacturing_date=None,
                                   expiration_date=None, package_id=None, owner_id=None,
                                   in_date=None):
        """ Increase or decrease `reserved_quantity` of a set of quants for a given set of
        product_id/location_id/lot_id/package_id/owner_id.

        :param product_id:
        :param location_id:
        :param quantity:
        :param lot_id:
        :param package_id:
        :param owner_id:
        :param datetime in_date: Should only be passed when calls to this method are done in
                                 order to move a quant. When creating a tracked quant, the
                                 current datetime will be used.
        :return: tuple (available_quantity, in_date as a datetime)
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, manufacturing_date=manufacturing_date,
                              expiration_date=expiration_date, package_id=package_id, owner_id=owner_id,
                              strict=True)

        if location_id.should_bypass_reservation():
            incoming_dates = []
        else:
            incoming_dates = [quant.in_date for quant in quants if quant.in_date and
                              float_compare(quant.quantity, 0, precision_rounding=quant.product_uom_id.rounding) > 0]
        if in_date:
            incoming_dates += [in_date]
        # If multiple incoming dates are available for a given lot_id/package_id/owner_id, we
        # consider only the oldest one as being relevant.
        if incoming_dates:
            in_date = min(incoming_dates)
        else:
            in_date = fields.Datetime.now()

        quant = None
        if quants:
            # see _acquire_one_job for explanations
            self._cr.execute("SELECT id FROM stock_quant WHERE id IN %s LIMIT 1 FOR NO KEY UPDATE SKIP LOCKED",
                             [tuple(quants.ids)])
            stock_quant_result = self._cr.fetchone()
            if stock_quant_result:
                quant = self.browse(stock_quant_result[0])

        if quant:
            quant.write({
                'quantity': quant.quantity + quantity,
                'in_date': in_date,
            })
        else:
            self.create({
                'product_id': product_id.id,
                'location_id': location_id.id,
                'quantity': quantity,
                'lot_id': lot_id and lot_id.id,
                'manufacturing_date': manufacturing_date,
                'expiration_date': expiration_date,
                'package_id': package_id and package_id.id,
                'owner_id': owner_id and owner_id.id,
                'in_date': in_date,
            })
        return self._get_available_quantity(product_id, location_id, lot_id=lot_id,
                                            manufacturing_date=manufacturing_date, expiration_date=expiration_date,
                                            package_id=package_id,
                                            owner_id=owner_id, strict=False, allow_negative=True), in_date

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, manufacturing_date=None,
                                   expiration_date=None, lot_id=None, package_id=None, owner_id=None, strict=False):
        """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(product_id, location_id, lot_id=lot_id, manufacturing_date=manufacturing_date,
                              expiration_date=expiration_date, package_id=package_id, owner_id=owner_id,
                              strict=True)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = self._get_available_quantity(product_id, location_id, lot_id=lot_id,
                                            manufacturing_date=manufacturing_date, expiration_date=expiration_date,
                                            package_id=package_id,
                                            owner_id=owner_id, strict=False, allow_negative=True)
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(_('It is not possible to reserve more products of %s than you have in stock.', product_id.display_name))
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
                raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.', product_id.display_name))
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity, precision_rounding=rounding):
                break
        return reserved_quants

    @api.model
    def _is_inventory_mode(self):
        """ Used to control whether a quant was written on or created during an
        "inventory session", meaning a mode where we need to create the stock.move
        record necessary to be consistent with the `inventory_quantity` field.
        """
        return self.env.context.get('inventory_mode') and self.user_has_groups('stock.group_stock_user')

    @api.model
    def create(self, vals):
        """ Override to handle the "inventory mode" and create a quant as
        superuser the conditions are met.
        """
        if self._is_inventory_mode() and any(f in vals for f in ['inventory_quantity', 'inventory_quantity_auto_apply']):
            allowed_fields = self._get_inventory_fields_create()
            if any(field for field in vals.keys() if field not in allowed_fields):
                raise UserError(_("Quant's creation is restricted, you can't do this operation."))

            inventory_quantity = vals.pop('inventory_quantity', False) or vals.pop(
                'inventory_quantity_auto_apply', False) or 0
            # Create an empty quant or write on a similar one.
            product = self.env['product.product'].browse(vals['product_id'])
            location = self.env['stock.location'].browse(vals['location_id'])
            lot_id = self.env['stock.production.lot'].browse(vals.get('lot_id'))
            manufacturing_date = self.env['stock.move.line'].browse(vals.get('manufacturing_date'))
            package_id = self.env['stock.quant.package'].browse(vals.get('package_id'))
            owner_id = self.env['res.partner'].browse(vals.get('owner_id'))
            quant = self._gather(product, location, lot_id=lot_id, manufacturing_date=manufacturing_date, package_id=package_id, owner_id=owner_id, strict=True)

            if quant:
                quant = quant[0].sudo()
            else:
                quant = self.sudo().create(vals)
            # Set the `inventory_quantity` field to create the necessary move.
            quant.inventory_quantity = inventory_quantity
            quant.user_id = vals.get('user_id', self.env.user.id)
            quant.inventory_date = fields.Date.today()

            return quant
        res = super(StockQuant, self).create(vals)
        if self._is_inventory_mode():
            res._check_company()
        return res

    # @api.depends("product_id", "amount_package")
    # def _inventory_quantity(self):
    #     for record in self:
    #         record.inventory_quantity = record.amount_package * record.product_id.weight
