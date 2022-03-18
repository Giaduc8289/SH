# Open ERP

# Coding convention & config environment
1. [Python](#python)
2. [Programming in Odoo](#odoo)
3. [Javascript](#javascript)
4. [Css](#css)
5. [Tech](#tech)
6. [Config env dev](#config)
7. [Add permission](#permission)
8. [Logger](#logger)
9. [Using JWT](#jwt)

## 1. Python <a name="python"></a>
###a. Import thư viện
Theo thứ tự: \
`1. Thư viện bên ngoài` \
`2. Thư viện của odoo` \
`3. Thư viện từ các module trong odoo`
+ Ví dụ 
```python
# 1 : imports of python lib
import base64
import re
import time
from datetime import datetime
# 2 : imports of odoo
import odoo
from odoo import api, fields, models, _ # alphabetically ordered
from odoo.tools.safe_eval import safe_eval as eval
# 3 : imports from odoo addons
from odoo.addons.website.models.website import slug
from odoo.addons.web.controllers.main import login_redirect
```
###b. Những mẹo khi làm việc với python
+ Mỗi file .py nên bắt đầu bằng `# -*- coding: utf-8 -*-`
+ Không nên sử dụng `.clone()`
```python
# bad
new_dict = my_dict.clone()
new_list = old_list.clone()
# good
new_dict = dict(my_dict)
new_list = list(old_list)
```
+ Python dictionary: creation and update
```python
# -- creation empty dict
my_dict = {}
my_dict2 = dict()

# -- creation with values
# bad
my_dict = {}
my_dict['foo'] = 3
my_dict['bar'] = 4
# good
my_dict = {'foo': 3, 'bar': 4}

# -- update dict
# bad
my_dict['foo'] = 3
my_dict['bar'] = 4
my_dict['baz'] = 5
# good
my_dict.update(foo=3, bar=4, baz=5)
my_dict = dict(my_dict, **my_dict2)
```
+ Đặt tên biến, hàm, lớp có ý nghĩa, loại bỏ các biến vô dụng:
```python
# pointless
schema = kw['schema']
params = {'schema': schema}
# simpler
params = {'schema': kw['schema']}
```
+ Đơn giản việc return tại nhiều nơi thay vì một:
```python
# Phức tạp và tạo ra biến axes dư thừa
def axes(self, axis):
        axes = []
        if type(axis) == type([]):
                axes.extend(axis)
        else:
                axes.append(axis)
        return axes

# clearer
def axes(self, axis):
        if type(axis) == type([]):
                return list(axis) # clone the axis
        else:
                return [axis] # single-element list
```
+ Hiểu những hàm cơ bản trong python (http://docs.python.org/library/functions.html)

+ List, dict: sử dụng `map, filter, sum, …`
```python
# not very good
cube = []
for i in res:
        cube.append((i['id'],i['name']))
# better
cube = [(i['id'], i['name']) for i in res]
```
+ Collections cũng có thể là boolean
```python
bool([]) is False
bool([1]) is True
bool([False]) is True

#Check colection 
if some_collection:
	...
#Thay cho: 
if len(some_collection):
	...
```
+ Iterate trong iterables:
```python
# creates a temporary list and looks bar
for key in my_dict.keys():
        "do something..."
# better
for key in my_dict:
        "do something..."
# accessing the key,value pair
for key, value in my_dict.items():
        "do something..."
```
+ Sử dụng hàm dict.setdefault hợp lý
```python
# longer.. harder to read
values = {}
for element in iterable:
    if element not in values:
        values[element] = []
    values[element].append(other_value)

# better.. use dict.setdefault method
values = {}
for element in iterable:
    values.setdefault(element, []).append(other_value)
```
+ Tất cả các method, class viết ra đều phải được comment rõ ràng bằng tiếng anh
+ Ngoài ra bạn có thể tham khảo thêm tại: https://www.python.org/dev/peps/pep-0008/

## 2. Programming in Odoo <a name="odoo"></a>
+ Không nên sử dụng create generators và decorators: chỉ sử dụng những gì được cung cấp bởi Odoo API.
+ Giống như trong Python, sử dụng các hàm `filtered, mapped, stored, ...` các phương thức dễ dàng đọc code và tăng hiệu năng.
+ Tạo ra các hàm sử lý nhiều bản ghi thay vì một.
```python
# self ở đây đóng vai trò là 1 hoặc nhiều bản ghi
def my_method(self):
    for record in self:
        record.do_cool_stuff()
```
Vấn đề hiệu năng khi làm việc với thống kê, sử dụng `search` hoặc `search_count` trong vòng lặp làm giảm hiệu năng. Bạn nên sử dụng hàm `read_group`, để compute tất cả các giá trị trong 1 request.
```python
def _compute_equipment_count(self):
    """ Count the number of equipment per category """
    equipment_data = self.env['hr.equipment'].read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
    mapped_data = dict([(m['category_id'][0], m['category_id_count']) for m in equipment_data])
    for category in self:
        category.equipment_count = mapped_data.get(category.id, 0)
```
+ Sử dụng context: \
Context không thể sửa đổi, để gọi hàm từ context khác bạn nên sử dụng `with_context`:
```python
records.with_context(new_context).do_stuff() # all the context is replaced
records.with_context(**additionnal_context).do_other_stuff() # additionnal_context values override native context ones
```  

> :warning: **Việc truyền parameter vào context có thể sẽ ảnh hưởng đến hiệu quả của side**: Vì values truyền vào sẽ từ động tạo ra trong 1 biến mới, một vào điều không lường trước được có thể xuất hiện. Ví dụ: khi gọi hàm `create()` của model với `default_my_field`
> trong context thì giá trị default của `my_field` được set. Nhưng trong suốt quá trình creation của context này, các object khác có field `my_field` thì mặc định trường này của các object này cũng được thiết lập bằng `default_my_field` của context.

+ Viết hàm có thể dễ dàng mở rộng code: \
Một function hoặc method không nên chứa quá nhiều code logic, nếu quá nhiều logic mình có thể suy nghĩ đến việc tách hàm ra thành các hàm nhỏ hơn
```python
# do not do this
# modifying the domain or criteria implies overriding whole method
def action(self):
    ...  # long method
    partners = self.env['res.partner'].search(complex_domain)
    emails = partners.filtered(lambda r: arbitrary_criteria).mapped('email')

# better but do not do this either
# modifying the logic forces to duplicate some parts of the code
def action(self):
    ...
    partners = self._get_partners()
    emails = partners._get_emails()

# better
# minimum override
def action(self):
    ...
    partners = self.env['res.partner'].search(self._get_partner_domain())
    emails = partners.filtered(lambda r: r._filter_partners()).mapped('email')
```  

+ Không bao giờ commit transaction: \
Odoo framework cung cấp transaction context bất cứ khi nào gọi RPC. Nguyên tắc: cursor sẽ được mở ra khi bắt đầu mỗi RPC được gọi và commit khi nó return trước khi trả lời RPC client \

Ví dụ:
```python
def execute(self, db_name, uid, obj, method, *args, **kw):
    db, pool = pooler.get_db_and_pool(db_name)
    # create transaction cursor
    cr = db.cursor()
    try:
        res = pool.execute_cr(cr, uid, obj, method, *args, **kw)
        cr.commit() # all good, we commit
    except Exception:
        cr.rollback() # error, rollback everything atomically
        raise
    finally:
        cr.close() # always close cursor opened manually
    return res
```

+ Sử dụng hàm translation chính xác:
```python
from odoo import _
```
```python
# good: plain strings
error = _('This record is locked!')

# good: strings with formatting patterns included
error = _('Record %s cannot be modified!', record)

# ok too: multi-line literal strings
error = _("""This is a bad multiline example
             about record %s!""", record)
error = _('Record %s cannot be modified' \
          'after being validated!', record)

# bad: tries to translate after string formatting
#      (pay attention to brackets!)
# This does NOT work and messes up the translations!
error = _('Record %s cannot be modified!' % record)

# bad: formatting outside of translation
# This won't benefit from fallback mechanism in case of bad translation
error = _('Record %s cannot be modified!') % record

# bad: dynamic string, string concatenation, etc are forbidden!
# This does NOT work and messes up the translations!
error = _("'" + que_rec['question'] + "' \n")

# bad: field values are automatically translated by the framework
# This is useless and will not work the way you think:
error = _("Product %s is out of stock!") % _(product.name)
# and the following will of course not work as already explained:
error = _("Product %s is out of stock!" % product.name)

# Instead you can do the following and everything will be translated,
# including the product name if its field definition has the
# translate flag properly set:
error = _("Product %s is not available!", product.name)
```
+ Symbols and Conventions
	- Sử dụng dấu `.` trong tên của model, tên model có prefix là tên module
		+ Khi định nghĩa Odoo Model: sử dụng danh từ số ít (vd: res.partner thay vì res.partnerS) 
		+ Khi định nghĩa Odoo Transient: sử dụng `<ten_model_goc>.<action>` (vd: `account.invoice.make` trong đó model gốc: `account.invoice`, action: `make`)
		+ Khi định nghĩa report model: sử dụng `<related_base_model>.report.<action>` dựa trên convention của Transient.
	- Odoo Python Class: Sử dụng quy tắc camelcase `class AccountInvoice(models.Model):`
	- Variable name:
		+ Sử dụng camelcase cho biến là model
		+ Sử dụng biến gạch dưới viết thường cho biến common
		+ Sử dụng biến common + `_id` hoặc `_ids` cho biến chưa id hoặc list id
	
		```python
		#Biến chứa model
		Partner = self.env['res.partner']
		#Biến common
		partners = Partner.browse(ids)
		#Biến chứa id của bản ghi
		partner_id = partners[0].id
		```
	- One2many và Many2many fields nên được đặt `_ids` vào sau (vd: `sale_order_line_ids`)
	- Many2one fields nên có _id theo sau (vd: `partner_id`)
	- Method Convention:
		+ Compute Field: `_compute_<field_name>`
		+ Search method: `_search_<field_name>`
		+ Default method: `_default_<field_name>`
		+ Selection method: `_selection_<field_name>`
		+ Onchange method: `_onchange_<field_name>`
		+ Constraint method: `_check_<constraint_name>`
		+ Action method: Bắt đầu bởi `action_.`. Vì nó sử dụng 1 bản ghi, thêm `self.ensure_one()` khi bắt đầu của hàm
	- Thứ tự các thuộc tính trong model \
		1, Private attributes (`_name, _description, _inherit, ...`) \
		2, Default method và `_default_get` \
		3, Định nghĩa fields \
		4, Compute, inverse và search methods theo thứ tự như định nghĩa fields \
		5, Selection method  \
		6, Contrains methods (`@api.constrains`) and onchange methods (`@api.onchange`) \
		7, CRUD methods (ORM overrides) \
		8, Action methods \
		9, Các hàm xử lý nghiệp vụ. 
	  
	Ví dụ: 
```python
class Event(models.Model):
	# Private attributes
	_name = 'event.event'
	_description = 'Event'

	# Default methods
	def _default_name(self):
		...

	# Fields declaration
	name = fields.Char(string='Name', default=_default_name)
	seats_reserved = fields.Integer(oldname='register_current', string='Reserved Seats',
		store=True, readonly=True, compute='_compute_seats')
	seats_available = fields.Integer(oldname='register_avail', string='Available Seats',
		store=True, readonly=True, compute='_compute_seats')
	price = fields.Integer(string='Price')
	event_type = fields.Selection(string="Type", selection='_selection_type')

	# compute and search fields, in the same order of fields declaration
	@api.depends('seats_max', 'registration_ids.state', 'registration_ids.nb_register')
	def _compute_seats(self):
		...

	@api.model
	def _selection_type(self):
		return []

	# Constraints and onchanges
	@api.constrains('seats_max', 'seats_available')
	def _check_seats_limit(self):
		...

	@api.onchange('date_begin')
	def _onchange_date_begin(self):
		...

	# CRUD methods (and name_get, name_search, ...) overrides
	def create(self, values):
		...

	# Action methods
	def action_validate(self):
		self.ensure_one()
		...

	# Business methods
	def mail_user_confirm(self):
		...
```
+ Directories:
	- data/: Thư mục chứ các file dữ liệu demo và data dạng xml
	- models/ : Định nghĩa các model tương ứng với table trên database
	- controllers/ : Chứa các controller (HTTP routes)
	- views/: Chứa các file template và giao diện người dùng
	- static/: Chứ các web assets bao gồm: css/, js/, img/, lib/, ...
	- wizard/: Nhóm lại transient models và view của nó
	- report/: Chứa báo cáo, models.
	- tests/: chứa các test Python
	
Cây thư mục chuẩn của một module trong odoo:

+ addons/plant_nursery/\
|-- `__init__.py` `(required)`\
|-- `__manifest__.py` `(required)`\
|-- controllers/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- `__init__.py`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery.py `(deprecated, replaced by plant_nursery.py) <module_name>.py`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- portal.py `(inheriting portal/controllers/portal.py) <inherited_module_name>.py`\
|-- data/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery_data.xml `<main_model>_data.xml`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery_demo.xml `<main_model>_demo.xml`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- mail_data.xml\
|-- models/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- `__init__.py`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery.py `(first main model) <module_name>.py`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order.py `(another main model)`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- res_partner.py `(inherited Odoo model)`\
|-- report/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- `__init__.py`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order_report.py\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order_report_views.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order_reports.xml `(report actions, paperformat, ...)`\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order_templates.xml `(xml report templates)`\
|-- security/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- ir.model.access.csv\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery_groups.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery_security.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order_security.xml\
|-- static/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- img/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- my_little_kitten.png\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- troll.jpg\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- lib/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- external_lib/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- src/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- js/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- widget_a.js\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- widget_b.js\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- scss/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- widget_a.scss\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- widget_b.scss\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- xml/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- widget_a.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- widget_a.xml\
|-- views/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- assets.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery_menus.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery_views.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_nursery_templates.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order_views.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- plant_order_templates.xml\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|-- res_partner_views.xml\
|-- wizard/\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--make_plant_order.py\
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--make_plant_order_views.xml\
  
+ Đặt tên XML IDs
	- Security, View and Action
		+ Menu: `<model_name>_menu` hoặc `<model_name>_menu_do_stuff` cho sub menu
		+ View: `<model_name>_view_<view_type>` trong đó `<view_type>': kanban, form, tree, search, ...
		+ Action: `<model_name>_action`, hoặc thêm hậu tố `_<detail>`
		+ window action: `<model_name>_action_view_<view_type>`
		+ Group: `<module_name>_group_<group_name>` trong đó group_name: ‘user’, ‘manager’, …
		+ Rule: `<model_name>_rule_<concerned_group>`
		ví dụ: 
```xml
<!-- views  -->
<odoo>
	<record id="model_name_view_form" model="ir.ui.view">
		<field name="name">model.name.view.form</field>
		...
	</record>
	
	<record id="model_name_view_kanban" model="ir.ui.view">
		<field name="name">model.name.view.kanban</field>
		...
	</record>
	
	<!-- actions -->
	<record id="model_name_action" model="ir.act.window">
		<field name="name">Model Main Action</field>
		...
	</record>
	
	<record id="model_name_action_child_list" model="ir.actions.act_window">
		<field name="name">Model Access Childs</field>
	</record>
	
	<!-- menus and sub-menus -->
	<menuitem
		id="model_name_menu_root"
		name="Main Menu"
		sequence="5"
	/>
	<menuitem
		id="model_name_menu_action"
		name="Sub Menu 1"
		parent="module_name.module_name_menu_root"
		action="model_name_action"
		sequence="10"
	/>
	
	<!-- security -->
	<record id="module_name_group_user" model="res.groups">
		...
	</record>
	
	<record id="model_name_rule_public" model="ir.rule">
		...
	</record>
	
	<record id="model_name_rule_company" model="ir.rule">
		...
	</record>
</odoo>
```
		+ Kế thừa view: `.inherit.{details}`
		
	Ví dụ: \
	Parent view
  
```xml
<record id="model_view_form" model="ir.ui.view">
	<field name="name">model.view.form.inherit.module2</field>
	<field name="inherit_id" ref="module1.model_view_form"/>
	...
</record>
```
Inherit view \

```xml
<record id="module2.model_view_form" model="ir.ui.view">
	<field name="name">model.view.form.module2</field>
	<field name="inherit_id" ref="module1.model_view_form"/>
	<field name="mode">primary</field>
	...
</record>
```

## 3. Javascript <a name="javascript"></a>
+ Sử dụng `use strict;` cho tất cả các file javascript
+ Sử dụng linter(jshint, ...)
+ Không sử dụng minified Javascript lib
+ Sử dụng camelcase cho tên class
## 4. Css <a name="css"></a>
+ Tất cả các class nên bắt đầu bởi `bio_<module_name>`
+ Tránh sử dụng id tag
+ Sử dụng Bootstrap native classes
+ Sử dụng underscore lowercase notation đặt tên class

## 5. Tech: <a name="tech"></a>
*  laguage: `Python`
*  db: `postgresql`
*  ui: `Odoo`
		
## 6. Config env dev <a name="config"></a>

*  Guideline: https://www.odoo.com/documentation/14.0/setup/install.html#source-install
*  Python: 3.9
*  Create file config:
	create file path /root/odoo/odoo.conf:
> 	[options]  
> 	db_host = localhost  
> 	db_port = 5432  
> 	db_user = odoo  
> 	db_password = admin@123  
> 	db_name = odoo_erp  
> 	addons_path=D:\Code\Odoo\odoo\addons,D:\Code\Odoo\odoo\custom  
> 	port = 8069  

### Pycharm: 
#### Run -> Edit configurations: 
>	script path: odoo\odoo-bin  
>	parameters: -c odoo.conf --dev xml
 
