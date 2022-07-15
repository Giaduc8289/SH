# Copyright 2019 C2i Change 2 improve - Eduardo Magdalena <emagdalena@c2i.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    bom_extend_id = fields.Many2one('mrp.bom.extend', string="Mix Recipe")

    @api.onchange('bom_extend_id')
    def onchange_bom_extend_id(self):
        for rec in self:
            rec.product_qty = rec.bom_extend_id.product_qty
            # rec.bom_line_ids = rec.bom_extend_id.bom_line_ids
            for bline in rec.bom_extend_id.bom_line_ids:
                self.env['mrp.bom.line'].sudo().create({
                    'product_id': bline.product_id.id,
                    'product_tmpl_id': bline.product_tmpl_id.id,
                    'company_id': bline.company_id.id,
                    'product_qty': bline.product_qty,
                    'product_uom_id': bline.product_uom_id.id,
                    'product_uom_category_id': bline.product_uom_category_id,
                    'bom_id': rec.id.origin,
                    'parent_product_tmpl_id': bline.parent_product_tmpl_id.id,
                })
            self.env['mrp.bom.line'].search([('bom_id', '=', rec.id.origin)])
            # rec.byproduct_ids = rec.bom_extend_id.byproduct_ids




