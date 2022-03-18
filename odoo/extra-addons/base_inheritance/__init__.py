from . import models


def post_init(cr, registry):
    """Rewrite ICP's to force groups"""
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    categories = env["product.category"].search([])
    for category in categories:
        category.code = env.ref('base_inheritance.sequence_code_product_category').next_by_id()
