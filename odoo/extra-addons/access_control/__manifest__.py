# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

{
    "name": "Access Control",
    "version": "15.0",
    "author": "hungtv2012@gmail.com",
    "sequence": "8",
    "license": "LGPL-3",
    # "category": "Hidden",
    "depends": ["account", 'base_inheritance'],
    "data": [
        'security/ir.model.access.csv',
        "views/access_control_view.xml",
    ],
    "installable": True,
    'application': True,
    "maintainers": ["hungtv2012@gmail.com"]
}
