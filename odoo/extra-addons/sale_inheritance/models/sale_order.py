# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tools.misc import formatLang
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now)

    amount_untaxed_1 = fields.Monetary(string='Price Amount', compute='_amount_price')
    amount_untaxed_2 = fields.Monetary(string='Discount Amount', compute='_amount_discount')

    @api.depends('order_line.price_total')
    def _amount_price(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = 0.0
            for line in order.order_line:
                if line.product_id.categ_id.id in (10, 11, 12):
                    amount_untaxed += line.price_subtotal
            order.update({
                'amount_untaxed_1': amount_untaxed,
            })

    @api.depends('order_line.price_total')
    def _amount_discount(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = 0.0
            for line in order.order_line:
                if line.product_id.categ_id.id not in (10, 11, 12):
                    amount_untaxed += line.price_subtotal
            order.update({
                'amount_untaxed_2': -amount_untaxed,
            })

    def _get_reward_values_discount_fixed_amount(self, program):
        total_amount = sum(self._get_base_order_lines(program).mapped('price_total'))
        fixed_amount = program._compute_program_amount('discount_fixed_amount', self.currency_id)
        #-----Tinh gia tri duoc chiet khau trong truong hop cau hinh chi tiet
        if program.config_detail:
            fixed_amount = program.coupon_detail_ids.filtered(lambda detail: self.partner_id in detail.partner_ids).discount_fixed_amount_detail
        #--------------------------------------------------------------------
        if total_amount < fixed_amount:
            return total_amount
        else:
            return fixed_amount


    def _get_reward_values_discount(self, program):
        if program.discount_type == 'fixed_amount':
            product_taxes = program.discount_line_product_id.taxes_id.filtered(lambda tax: tax.company_id == self.company_id)
            taxes = self.fiscal_position_id.map_tax(product_taxes)
            #-----Tinh toan khoi luong duoc chiet khau
            order_lines = (self.order_line - self._get_reward_lines()).filtered(lambda x: program._get_valid_products(x.product_id))
            max_product_qty = sum(order_lines.mapped('product_uom_qty'))
            #-----------------------------------------
            return [{
                'name': _("Discount: %s", program.name),
                'product_id': program.discount_line_product_id.id,
                'price_unit': - self._get_reward_values_discount_fixed_amount(program),
                'product_uom_qty': max_product_qty if program.discount_for_amount else 1.0,#1.0,
                'product_uom': program.discount_line_product_id.uom_id.id,
                'is_reward_line': True,
                'tax_id': [(4, tax.id, False) for tax in taxes],
            }]
        reward_dict = {}
        lines = self._get_paid_order_lines()
        amount_total = sum(self._get_base_order_lines(program).mapped('price_subtotal'))
        if program.discount_apply_on == 'cheapest_product':
            line = self._get_cheapest_line()
            if line:
                discount_line_amount = min(line.price_reduce * (program.discount_percentage / 100), amount_total)
                if discount_line_amount:
                    taxes = self.fiscal_position_id.map_tax(line.tax_id)

                    reward_dict[line.tax_id] = {
                        'name': _("Discount: %s", program.name),
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                        'product_uom_qty': 1.0,
                        'product_uom': program.discount_line_product_id.uom_id.id,
                        'is_reward_line': True,
                        'tax_id': [(4, tax.id, False) for tax in taxes],
                    }
        elif program.discount_apply_on in ['specific_products', 'on_order']:
            if program.discount_apply_on == 'specific_products':
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['coupon.program'].search([('reward_type', '=', 'product'), ('reward_product_id', 'in', program.discount_specific_product_ids.ids)]).mapped('discount_line_product_id')
                lines = lines.filtered(lambda x: x.product_id in (program.discount_specific_product_ids | free_product_lines))

            # when processing lines we should not discount more than the order remaining total
            currently_discounted_amount = 0
            for line in lines:
                discount_line_amount = min(self._get_reward_values_discount_percentage_per_line(program, line), amount_total - currently_discounted_amount)

                if discount_line_amount:

                    if line.tax_id in reward_dict:
                        reward_dict[line.tax_id]['price_unit'] -= discount_line_amount
                    else:
                        taxes = self.fiscal_position_id.map_tax(line.tax_id)

                        reward_dict[line.tax_id] = {
                            'name': _(
                                "Discount: %(program)s - On product with following taxes: %(taxes)s",
                                program=program.name,
                                taxes=", ".join(taxes.mapped('name')),
                            ),
                            'product_id': program.discount_line_product_id.id,
                            'price_unit': - discount_line_amount if discount_line_amount > 0 else 0,
                            'product_uom_qty': 1.0,
                            'product_uom': program.discount_line_product_id.uom_id.id,
                            'is_reward_line': True,
                            'tax_id': [(4, tax.id, False) for tax in taxes],
                        }
                        currently_discounted_amount += discount_line_amount

        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()


class ReportSaleOrder(models.Model):
    _name = 'report.sale.order'
    _description = "Report Sale Order"
    _rec_name = 't_date'

    f_date = fields.Date('Date from:', )
    t_date = fields.Date('Date to:')

    @api.constrains('f_date', 't_date')
    def action_print_report(self):
        action = self.env["ir.actions.actions"]._for_xml_id('sale_inheritance.action_orders_1')
        action['domain'] = [('date_order', '>=', self.f_date), ('date_order', '<=', self.t_date)]

        return action