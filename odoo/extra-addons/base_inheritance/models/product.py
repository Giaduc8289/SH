from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_kind = fields.Many2one('product.kind', 'Product Kind', change_default=True,
                                   help="Select kind for the current product")
    product_line = fields.Selection([('cavi', 'Cavi Feed'), ('biochemistry', 'Biochemistry'), ('bonong', 'Bồ Nông')],
                                    string='Product line', default='biochemistry')
    product_spec = fields.Char(string='Spec of product')
    percent_protein = fields.Integer(string='Percent of protein')
    specifications = fields.Integer(string='Specifications (Kg)')
    cus_price = fields.Float(string='Giá hóa đơn (Đ/kg)')
    cus_price_package = fields.Float(string='Giá hóa đơn (Đ/bao)', compute="_cus_price_package")
    use_discount = fields.Boolean(string='Chiết khấu', default=True)

    @api.depends("specifications", "cus_price")
    def _cus_price_package(self):
        for record in self:
            record.cus_price_package = record.specifications * record.cus_price

    # @api.onchange("specifications")
    # def _onchange_specifications(self):
    #     self.cus_price_package = self.specifications * self.cus_price
    #
    # @api.onchange("cus_price")
    # def _onchange_cus_price(self):
    #     self.cus_price_package = self.specifications * self.cus_price


class ProductTemplate(models.Model):
    _inherit = "product.product"

    product_kind = fields.Many2one('product.kind', 'Product Kind', change_default=True,
                                   help="Select kind for the current product")

    @api.model
    def create(self, vals_list):
        if 'default_code' not in vals_list or not vals_list['default_code']:
            if 'detailed_type' in vals_list and vals_list['detailed_type'] == 'consu':
                seq = self.env.ref('base_inheritance.sequence_code_product_consumable')
                vals_list['default_code'] = seq.next_by_id() or 'TD'
            elif 'detailed_type' in vals_list and vals_list['detailed_type'] == 'service':
                seq = self.env.ref('base_inheritance.sequence_code_product_service')
                vals_list['default_code'] = seq.next_by_id() or 'DV'
            elif 'detailed_type' in vals_list and vals_list['detailed_type'] == 'product':
                seq = self.env.ref('base_inheritance.sequence_code_product_product')
                vals_list['default_code'] = seq.next_by_id() or 'MH'
            else:
                seq = self.env.ref('base_inheritance.sequence_code_product_another')
                vals_list['default_code'] = seq.next_by_id() or 'OT'
        return super(ProductTemplate, self).create(vals_list)


class ProductKind(models.Model):
    _name = "product.kind"
    _description = "Kind of product"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    code = fields.Char('Code', index=True, required=True, default="New", readonly=True)
    name = fields.Char('Name', index=True, required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    parent_id = fields.Many2one('product.kind', 'Parent Kind', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('product.kind', 'parent_id', 'Child Kinds')
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this kind (Does not consider the children kinds)")
    status = fields.Boolean(string='Status', default=True)
    description = fields.Char(string='Description')

    @api.model
    def create(self, vals_list):
        if ('code' in vals_list and vals_list['code'] == 'New') or 'code' not in vals_list:
            seq = self.env.ref('base_inheritance.sequence_code_product_kind')
            vals_list['code'] = seq.next_by_id() or "KP"
        return super(ProductKind, self).create(vals_list)

    @api.model
    def update_code(self, data):
        seq = self.env.ref('base_inheritance.sequence_code_product_kind')
        temp = self.browse(data)
        temp.code = seq.next_by_id() or "KP"

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_product_count(self):
        read_group_res = self.env['product.template'].read_group([('product_kind', 'child_of', self.ids)],
                                                                 ['product_kind'], ['product_kind'])
        group_data = dict((data['product_kind'][0], data['kind_id_count']) for data in read_group_res)
        for kind in self:
            product_count = 0
            for sub_kind_id in kind.search([('id', 'child_of', kind.ids)]).ids:
                product_count += group_data.get(sub_kind_id, 0)
            kind.product_count = product_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive categories.'))

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super().name_get()

    @api.ondelete(at_uninstall=False)
    def _unlink_except_default_category(self):
        main_category = self.env.ref('product.product_category_all')
        if main_category in self:
            raise UserError(_("You cannot delete this product category, it is the default generic category."))


class ProductCategory(models.Model):
    _inherit = "product.category"

    code = fields.Char('Code', index=True, required=True, default='New', readonly=True)
    status = fields.Boolean(string='Status', default=True)
    description = fields.Char(string='Description')

    @api.model
    def create(self, vals_list):
        if ('code' in vals_list and vals_list['code'] == 'New') or 'code' not in vals_list:
            seq = self.env.ref('base_inheritance.sequence_code_product_category')
            vals_list['code'] = seq.next_by_id() or "PC"
        return super(ProductCategory, self).create(vals_list)

