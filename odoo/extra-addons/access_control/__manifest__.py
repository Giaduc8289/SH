# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Access Control",
    "version": "15.0",
    "author": "hungtv2012@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    # "category": "Hidden",
    "depends": ["account", 'base_inheritance', 'quality_assurance'],
    "data": [
        'security/access_control.xml',
        'security/ir.model.access.csv',
        "data/ir_sequence.xml",
        "views/access_control_view.xml",
        "report/access_control_report.xml",
        "report/access_control_report_templates.xml",
        "report/weight_report_templates.xml",
        "views/sale_views.xml",
        "views/purchase_views.xml",
        "views/stock_menu_views.xml",
        "views/quality_view.xml",
        "report/report_access_control.xml",
    ],
    "installable": True,
    'application': True,
    "maintainers": ["hungtv2012@gmail.com"]
}
