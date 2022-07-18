# Copyright 2019 C2i Change 2 improve - Eduardo Magdalena <emagdalena@c2i.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    bom_extend_id = fields.Many2one('mrp.bom.extend', string="Bill of Material")

    @api.onchange('bom_extend_id')
    def onchange_bom_extend_id(self):
        # mrp_bom_current = self.env["mrp.bom"].browse(self.id)
        # for rec in self:
            self.product_qty = self.bom_extend_id.product_qty
            # rec.bom_line_ids = rec.bom_extend_id.bom_line_ids
            b_list = []
            for bline in self.bom_extend_id.bom_line_ids:
                b_list += [{
                    'product_id': bline.product_id.id,
                    'product_tmpl_id': bline.product_tmpl_id.id,
                    'company_id': bline.company_id.id,
                    'product_qty': bline.product_qty,
                    'product_uom_id': bline.product_uom_id.id,
                    'product_uom_category_id': bline.product_uom_category_id,
                    'bom_id': self.id,
                    'parent_product_tmpl_id': bline.parent_product_tmpl_id.id,
                }]
            self.bom_line_ids = [(7, 0)] + [(0, 0, value) for value in b_list]
            # rec.byproduct_ids = rec.bom_extend_id.byproduct_ids
            w_list = []
            for wline in self.bom_extend_id.operation_ids:
                w_list += [{
                    'name': wline.name,
                    'active': wline.active,
                    'workcenter_id': wline.workcenter_id.id,
                    'sequence': wline.sequence,
                    'company_id': wline.company_id.id,
                    'bom_id': self.id,
                    'worksheet_type': wline.worksheet_type,
                    'note': wline.note,
                    'worksheet': wline.worksheet,
                    'worksheet_google_slide': wline.worksheet_google_slide,
                    'time_mode': wline.time_mode,
                    'time_mode_batch': wline.time_mode_batch,
                    'time_computed_on': wline.time_computed_on,
                    'time_cycle_manual': wline.time_cycle_manual,
                    'time_cycle': wline.time_cycle,
                    'workorder_count': wline.workorder_count,
                    'workorder_ids': wline.workorder_ids,
                    'possible_bom_product_template_attribute_value_ids': wline.possible_bom_product_template_attribute_value_ids,
                    'bom_product_template_attribute_value_ids': wline.bom_product_template_attribute_value_ids,
                }]
            self.operation_ids = [(18, 0)] + [(0, 0, value) for value in w_list]

