# coding: utf-8
from __future__ import unicode_literals
from flask.ext.admin.form import Select2Widget
from wtforms import fields
from ..kforms.forms import Form
import datetime

class DomainForm(Form):
	_id = fields.TextField('域名')
	name = fields.TextField('名称')


class DomainEditForm(Form):
	_id = fields.TextField('域名')
	name = fields.TextField('名称')


class CateForm(Form):
	url = fields.TextField('链接')
	name = fields.TextField('名称')


class TplForm(Form):
	_id = fields.TextField('模板')
	title_selector = fields.TextField('标题css')
	source_selector = fields.TextField('来源css')
	content_selector = fields.TextField('正文css')


class TplEditForm(Form):
	_id = fields.TextField('模板')
	title_selector = fields.TextField('标题css')
	source_selector = fields.TextField('来源css')
	content_selector = fields.TextField('正文css')


class ArtForm(Form):
	url = fields.TextField('链接')
	title = fields.TextField('标题')
	src_name = fields.TextField('来源')
	src_link = fields.TextField('来源链接')


class RoleForm(Form):
	name = fields.TextField('name')
	decs = fields.TextField('decs')

class  UserForm(Form):
	name = fields.TextField('Name')
	password = fields.TextField('Password')
	
	def __unicode__(self):
		return self.name

class TaskForm(Form):
	title = fields.TextField('title')
	content = fields.TextField('content')
	user_id = fields.SelectField('User', widget=Select2Widget())
	pubtime = fields.DateTimeField(default=datetime.datetime.now)

class RecodeForm(Form):
	title = fields.TextField('title')
	content = fields.TextField('content')
	pubtime = fields.DateTimeField(default=datetime.datetime.now)
	task_id = fields.SelectField('Task', widget=Select2Widget())
