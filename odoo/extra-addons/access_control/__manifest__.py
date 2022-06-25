# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Access Control",
    "version": "15.0",
    "author": "hungtv2012@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    # "category": "Hidden",
    "depends": ['account', 'base_inheritance', 'quality_assurance', 'sale_inheritance', 'purchase_inheritance'],
    "data": [
        'security/access_control.xml',
        'security/ir.model.access.csv',
        "data/ir_sequence.xml",
        "views/access_control_view.xml",
        "views/sale_views.xml",
        "views/purchase_views.xml",
        "views/stock_menu_views.xml",
        "views/quality_view.xml",
        "wizard/access_control_report.xml",
        "wizard/access_control_report_templates.xml",
        "wizard/weight_vehicle_report_templates.xml",
        "wizard/access_control_report_view.xml",
    ],
    "installable": True,
    'application': True,
    "maintainers": ["hungtv2012@gmail.com"]
}
