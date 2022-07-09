# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)
{
    "name": "Employee Management",
    "version": "1.0",
    "author": "AnhPT",
    "license": "LGPL-3",
    "depends": [
        'hr',
        'base_address_extended',
        'base_address_city',
        'base_inheritance',
        'hr_contract'
    ],
    "data": [
        'data/ir_sequence.xml',
        'views/view_list_hr_tree.xml',
        'views/department_info.xml',
        'views/job_info.xml',
        'views/view_hr_job_form_inheritance.xml',
        'views/employee_info.xml',
        'security/security.xml',
        # 'security/ir.model.access.csv',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "maintainers": [""],
    "description": "Quản lý thông tin nhân viên"
}
