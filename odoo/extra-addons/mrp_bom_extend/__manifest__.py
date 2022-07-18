# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Mrp Bom Extend",
    "version": "15.0",
    "author": "hungtv2012@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    # "category": "Hidden",
    "depends": ['mrp', 'mrp_inheritance'],
    "data": [
        'security/ir.model.access.csv',
        "views/mrp_bom_view.xml",
        "views/mrp_bom_extend_views.xml",
    ],
    "installable": True,
    'application': True,
    "maintainers": ["hungtv2012@gmail.com"]
}
