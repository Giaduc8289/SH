# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # def _get_reward_values_discount_fixed_amount(self, program):
    #     total_amount = sum(self._get_base_order_lines(program).mapped('price_total'))
    #     fixed_amount = program._compute_program_amount('discount_fixed_amount', self.currency_id)
    #     #-----Tinh gia tri duoc chiet khau trong truong hop cau hinh chi tiet
    #     if program.config_detail:
    #         fixed_amount = program._compute_program_amount('discount_fixed_amount_detail', self.currency_id)
    #     #--------------------------------------------------------------------
    #     if total_amount < fixed_amount:
    #         return total_amount
    #     else:
    #         return fixed_amount
    #
    # def _is_valid_partner_detail(self, partner):
    #     if self.env['coupon.detail'].partner_ids and self.rule_partners_domain != '[]':
    #         domain = ast.literal_eval(self.rule_partners_domain) + [('id', '=', partner.id)]
    #         return bool(self.env['res.partner'].search_count(domain))
    #     else:
    #         return True
    #
    # def _remove_invalid_reward_lines(self):
    #     """ Find programs & coupons that are not applicable anymore.
    #         It will then unlink the related reward order lines.
    #         It will also unset the order's fields that are storing
    #         the applied coupons & programs.
    #         Note: It will also remove a reward line coming from an archive program.
    #     """
    #     self.ensure_one()
    #     order = self
    #
    #     applied_programs = order._get_applied_programs()
    #     applicable_programs = self.env['coupon.program']
    #     if applied_programs:
    #         applicable_programs = order._get_applicable_programs() + order._get_valid_applied_coupon_program()
    #         applicable_programs = applicable_programs._keep_only_most_interesting_auto_applied_global_discount_program()
    #     programs_to_remove = applied_programs - applicable_programs
    #
    #     reward_product_ids = applied_programs.discount_line_product_id.ids
    #     # delete reward line coming from an archived coupon (it will never be updated/removed when recomputing the order)
    #     invalid_lines = order.order_line.filtered(lambda line: line.is_reward_line and line.product_id.id not in reward_product_ids)
    #
    #     if programs_to_remove:
    #         product_ids_to_remove = programs_to_remove.discount_line_product_id.ids
    #
    #         if product_ids_to_remove:
    #             # Invalid generated coupon for which we are not eligible anymore ('expired' since it is specific to this SO and we may again met the requirements)
    #             self.generated_coupon_ids.filtered(lambda coupon: coupon.program_id.discount_line_product_id.id in product_ids_to_remove).write({'state': 'expired'})
    #
    #         # Reset applied coupons for which we are not eligible anymore ('valid' so it can be use on another )
    #         coupons_to_remove = order.applied_coupon_ids.filtered(lambda coupon: coupon.program_id in programs_to_remove)
    #         coupons_to_remove.write({'state': 'new'})
    #
    #         # Unbind promotion and coupon programs which requirements are not met anymore
    #         order.no_code_promo_program_ids -= programs_to_remove
    #         order.code_promo_program_id -= programs_to_remove
    #
    #         if coupons_to_remove:
    #             order.applied_coupon_ids -= coupons_to_remove
    #
    #         # Remove their reward lines
    #         if product_ids_to_remove:
    #             invalid_lines |= order.order_line.filtered(lambda line: line.product_id.id in product_ids_to_remove)
    #
    #     invalid_lines.unlink()




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
