# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Base inheritance",
    "version": "15.0",
    "author": "hieutv.199x@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    "category": "Hidden",
    "depends": ["base", "web", "account", "purchase", "stock", "sale_management"],
    "data": [
        'security/ir.model.access.csv',
        "data/ir_sequence.xml",
        "data/product_data.xml",
        "views/login_layout.xml",
        "views/product_view.xml",
        "views/res_partner_view.xml",
        "views/stock_warehouse_views.xml",
        "views/header_inheritance.xml",
        "data/res.country.location.csv",
        "views/res_bank_views.xml"
    ],
    "installable": True,
    "maintainers": ["hieutv.199x@gmail.com"],
    "post_init_hook": "post_init",
}
