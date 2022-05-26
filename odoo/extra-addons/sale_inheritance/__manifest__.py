# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Sales inheritance",
    "version": "15.0",
    "author": "anhnth.mta@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    "category": "Hidden",
    "depends": ["base_inheritance", "sale", 'coupon', "sale_coupon", "access_control"],
    "data": [
        'security/ir.model.access.csv',
        "report/sale_report_views.xml",
        "views/sale_order_views.xml",
        "views/sale_views.xml",
        "views/coupon_program_views.xml",
        "report/sale_report_templates.xml",
        "views/preview_sale.xml",
    ],
    "installable": True,
    "maintainers": ["anhnth.mta@gmail.com"]
}
