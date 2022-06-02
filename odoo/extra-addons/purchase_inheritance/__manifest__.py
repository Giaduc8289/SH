# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Purchase inheritance",
    "version": "15.0",
    "author": "hieutv.199x@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    "category": "Hidden",
    "depends": ["base", "web", "base_inheritance", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_report_views.xml",
        "views/product_template_view.xml",
        "report/report_purchase_order_view.xml",
        "report/purchase_report_templates.xml",
    ],
    "installable": True,
    "maintainers": ["hieutv.199x@gmail.com"]
}
