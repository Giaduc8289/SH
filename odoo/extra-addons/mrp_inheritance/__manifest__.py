# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "mrp inheritance",
    "version": "15.0",
    "author": "hungtv2012@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    # "category": "Hidden",
    "depends": ['account', 'base_inheritance', 'mrp'],
    "data": [
        "security/mrp_bom_security.xml",
        "report/mrp_production_templates.xml",
        "view/mrp_report_views_main.xml",
        "view/mrp_bom_views.xml",
    ],
    "installable": True,
    'application': True,
    "maintainers": ["hungtv2012@gmail.com"]
}
