# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Sales inheritance",
    "version": "15.0",
    "author": "anhnth.mta@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    "category": "Hidden",
    "depends": ["base_inheritance", "sale", 'coupon', "sale_coupon", "product"],
    "data": [
        'security/ir.model.access.csv',
        "wizard/postpaid_discount.xml",
        "wizard/report_discount_coupon.xml",
        "wizard/report_discount_coupon_document.xml",
        "views/product_pricelist_views.xml",
        "report/report_pricelist_templates.xml",
        "wizard/sale_report_views.xml",
        "views/sale_order_views.xml",
        "views/sale_views.xml",
        "views/coupon_program_views.xml",
        "report/sale_report_templates.xml",
        "views/preview_sale.xml",
        "wizard/report_sale_order_template.xml",
        "wizard/report_select_sale_order_template.xml",
        "report/sale_report.xml",
        "wizard/sale_summary_report_temp.xml",
        "wizard/sale_summary_report_view.xml",
        "wizard/report_postpaid_discount_document.xml"
    ],
    "installable": True,
    "maintainers": ["anhnth.mta@gmail.com"]
}
