# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Purchase inheritance",
    "version": "15.0",
    "author": "hieutv.199x@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    "category": "Hidden",
    "depends": ["base", "web", "base_inheritance", "purchase", 'mrp'],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
        "report/purchase_report_templates.xml",
        "wizard/purchase_report_views.xml",
        "views/purchase_report_template.xml",
        "wizard/report_purchase_order_view.xml",
        "views/purchase_quotation_templates.xml",
    ],
    "installable": True,
    "maintainers": ["hieutv.199x@gmail.com"]
}
