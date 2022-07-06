# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    _order = "product_id"

    product_default_code = fields.Char(related="product_template_id.default_code", string="Mã hàng")
    product_weight = fields.Float(related="product_template_id.weight", string="Quy cách")
    amount_package = fields.Integer(string='Số bao')

    @api.onchange("amount_package")
    def _amount_package(self):
        for record in self:
            if (record.product_weight == 0):
                record.amount_package = 0
            else:
                record.product_uom_qty = int(record.amount_package * record.product_weight)

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                ptav.price_extra and
                ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )
        # -----Hiệu chỉnh cách lấy giá trong bảng giá
        # if self.order_id.pricelist_id.discount_policy == 'with_discount':
        #     return product.with_context(pricelist=self.order_id.pricelist_id.id, uom=self.product_uom.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                           self.product_uom_qty,
                                                                                           self.product_uom,
                                                                                           self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price

        #-----Hiệu chỉnh cách lấy giá trong bảng giá
        pricelist_item = self.order_id.pricelist_id.id
        data = self.env['product.pricelist.item'].search([('pricelist_id', '=', pricelist_item)
                                                             , ('product_tmpl_id', '=', product.id)], limit=1)
        if data:
            base_price, currency = data[0].final_price, data[0].currency_id
            final_price = data[0].final_price

        return max(base_price, final_price)