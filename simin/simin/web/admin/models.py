# coding: utf-8# coding: utf-8
from collections import OrderedDict
import datetime
from flask import request, redirect
from flask.ext.admin.contrib.pymongo import ModelView as _ModelView
from flask.ext.admin.contrib.sqla import ModelView as _SModelView
from flask.ext.admin.babel import gettext, ngettext, lazy_gettext
from flask.ext.admin.base import expose
from flask.ext.admin.model.helpers import get_mdict_item_or_list
from flask.ext.admin.helpers import get_form_data, validate_form_on_submit, get_redirect_target
from flask.ext.admin.actions import action
from flask.ext.admin.form import FormOpts, rules
from .deals import DealsMixin


class ModelView(_ModelView, DealsMixin):
	
	list_template = 'simin_admin/list.html'
	create_template = 'simin_admin/create.html'
	edit_template = 'simin_admin/edit.html'
	detail_template = 'simin_admin/detail.html'

	can_detail = True
	detail_list = None

	more_views = []

	def __init__(self, coll,
				 name=None, category=None, endpoint=None, url=None):
		super(ModelView, self).__init__(coll,
			name=name,
			category=category,
			endpoint=endpoint,
			url=url,
		)
		self.init_deals()

	@expose('/detail/')
	def detail_view(self):
		id = get_mdict_item_or_list(request.args, 'id')
		return_url = get_mdict_item_or_list(request.args, 'return_url')
		
		if id is None:
			return redirect(return_url)

		model = self.get_one(id)

		if model is None:
			return redirect(return_url)

		if self.detail_list is None:
			data = model
		else:
			data = OrderedDict((x, model.get(x, '')) for x in self.detail_list)

		self.format(data)
		form_opts = FormOpts(widget_args=self.form_widget_args,
				form_rules=self._form_edit_rules)
		return self.render(
			self.detail_template,
			model=model,
			data=data,
		)

	def format(self, data):
		for k, v in data.iteritems():
			if isinstance (v, float):
				data[k] = datetime.datetime.utcfromtimestamp(v).strftime( '%Y-%m-%d %H:%M:%S' ) 
			elif isinstance(v, list):
				data[k] = ', '.join(v)

	@expose('/edit/', methods=('GET', 'POST'))
	def edit_view(self):
		"""
			Edit model view
		"""
		return_url = get_redirect_target() or self.get_url('.index_view')

		if not self.can_edit:
			return redirect(return_url)

		id = get_mdict_item_or_list(request.args, 'id')
		if id is None:
			return redirect(return_url)

		model = self.get_one(id)

		if model is None:
			return redirect(return_url)

		form = self.edit_form(obj=model)

		if self.validate_form(form):
			if self.update_model(form, model):
				if '_continue_editing' in request.form:
					flash(gettext('Model was successfully saved.'))
					return redirect(request.url)
				else:
					return redirect(return_url)

		form_widget_args = self.form_widget_args
		if hasattr(self, 'edit_form_widget_args'):
			form_widget_args = self.edit_form_widget_args

		form_opts = FormOpts(widget_args=form_widget_args,
							 form_rules=self._form_edit_rules)

		return self.render(self.edit_template,
						   model=model,
						   form=form,
						   form_opts=form_opts,
						   return_url=return_url)

	def validate_form(self, form):
		return validate_form_on_submit(form)


	@expose('/')
	def index_view(self):
		view_args = self._get_list_extra_args()
		sort_column = self._get_column_by_idx(view_args.sort)
		if sort_column is not None:
			sort_column = sort_column[0]

		count, data = self.get_list(view_args.page, sort_column, view_args.sort_desc,
									view_args.search, view_args.filters)

		num_pages = count // self.page_size
		if count % self.page_size != 0:
			num_pages += 1

		def pager_url(p):
			if p == 0:
				p = None
			return self._get_list_url(view_args.clone(page=p))

		def sort_url(column, invert=False):
			desc = None

			if invert and not view_args.sort_desc:
				desc = 1

			return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

		actions, actions_confirmation = self.get_actions_list()
		deals = self.get_deals()

		clear_search_url = self._get_list_url(view_args.clone(page=0,
															  sort=view_args.sort,
															  sort_desc=view_args.sort_desc,
															  search=None,
															  filters=None))

		return self.render(self.list_template,
							   data=data,
							   # List
							   list_columns=self._list_columns,
							   sortable_columns=self._sortable_columns,
							   # Stuff
							   enumerate=enumerate,
							   get_pk_value=self.get_pk_value,
							   get_value=self.get_list_value,
							   return_url=self._get_list_url(view_args),
							   # Pagination
							   count=count,
							   pager_url=pager_url,
							   num_pages=num_pages,
							   page=view_args.page,
							   # Sorting
							   sort_column=view_args.sort,
							   sort_desc=view_args.sort_desc,
							   sort_url=sort_url,
							   # Search
							   search_supported=self._search_supported,
							   clear_search_url=clear_search_url,
							   search=view_args.search,
							   # Filters
							   filters=self._filters,
							   filter_groups=self._filter_groups,
							   active_filters=view_args.filters,

							   # Actions
							   actions=actions,
							   actions_confirmation=actions_confirmation,
							   
							   #deals
							   deals=deals)


class SModelView(_SModelView, DealsMixin):
	"""
		SQLAlchemy 模型管理类
	"""

	# 设置模板
	list_template = 'simin_admin/list.html'
	create_template = 'simin_admin/create.html'
	edit_template = 'simin_admin/edit.html'
	detail_template = 'simin_admin/detail.html'
	create_ajax_template = 'simin_admin/create-ajax.html'
	edit_ajax_template = 'simin_admin/edit-ajax.html'
	detail_ajax_template = 'simin_admin/detail-ajax.html'

	create_ajax = True
	edit_ajax = True
	detail_ajax = True

	# 是否显示详情
	can_detail = True
	detail_list = None

	# 更多视图
	more_views = []

	def __init__(self, model, session, 
			name=None, category=None, endpoint=None, url=None):
		super(SModelView, self).__init__(model, session,
				name=name, category=category, endpoint=endpoint, url=url)
		self.init_deals()

	@expose('/new/', methods=('GET', 'POST'))
	def create_view(self):
		return_url = get_redirect_target() or self.get_url('.index_view')
		if not self.can_create:
			return redirect(return_url)

		form = self.create_form()

		if self.validate_form(form):
			if self.create_model(form):
				if '_add_another' in request.form:
					flash(gettext('Model was successfully created.'))
					return redirect(request.url)
				else:
					return redirect(return_url)

		form_opts = FormOpts(widget_args=self.form_widget_args,
							 form_rules=self._form_create_rules)

		template = self.create_ajax_template if self.create_ajax == True else self.create_template
		return self.render(template,
						   form=form,
						   form_opts=form_opts,
						   return_url=return_url)

	@expose('/detail/')
	def detail_view(self):
		id = get_mdict_item_or_list(request.args, 'id')
		return_url = get_mdict_item_or_list(request.args, 'return_url')
		
		if id is None:
			return redirect(return_url)

		model = self.get_one(id)
		if model is None:
			return redirect(return_url)

		if self.detail_list is None:
			data = model
		else:
			data = OrderedDict((x, model.get(x, '')) for x in self.detail_list)

		data = self.format(data)
		form_opts = FormOpts(widget_args=self.form_widget_args,
				form_rules=self._form_edit_rules)

		template = self.detail_ajax_template if self.detail_ajax == True else self.detail_template
		return self.render(template, model=model, data=data)

	def format(self, data):
		if isinstance(data, dict):
			print 'data is dict'
		else:
			data = sa_obj_to_dict(data)
		for k, v in data.iteritems():
			if isinstance (v, float):
				data[k] = datetime.datetime.utcfromtimestamp(v).strftime( '%Y-%m-%d %H:%M:%S' ) 
			elif isinstance(v, list):
				data[k] = ', '.join(v)
		return data

	
	@expose('/edit/', methods=('GET', 'POST'))
	def edit_view(self):
		return_url = get_redirect_target() or self.get_url('.index_view')
		if not self.can_edit:
			return redirect(return_url)

		id = get_mdict_item_or_list(request.args, 'id')
		if id is None:
			return redirect(return_url)

		model = self.get_one(id)
		if model is None:
			return redirect(return_url)

		form = self.edit_form(obj=model)
		if self.validate_form(form):
			if self.update_model(form, model):
				if '_continue_editing' in request.form:
					flash(gettext('Model was successfully saved.'))
					return redirect(request.url)
				else:
					return redirect(return_url)

		form_widget_args = self.form_widget_args
		if hasattr(self, 'edit_form_widget_args'):
			form_widget_args = self.edit_form_widget_args

		form_opts = FormOpts(widget_args=form_widget_args,
							 form_rules=self._form_edit_rules)

		template = self.edit_ajax_template if self.edit_ajax == True else self.edit_template
		return self.render(template, model=model, form=form, form_opts=form_opts, return_url=return_url)

	def validate_form(self, form):
		return validate_form_on_submit(form)

	@expose('/')
	def index_view(self):
		view_args = self._get_list_extra_args()
		sort_column = self._get_column_by_idx(view_args.sort)
		if sort_column is not None:
			sort_column = sort_column[0]

		count, data = self.get_list(view_args.page, sort_column, view_args.sort_desc,
									view_args.search, view_args.filters)
		num_pages = count // self.page_size
		if count % self.page_size != 0:
			num_pages += 1

		def pager_url(p):
			if p == 0:
				p = None
			return self._get_list_url(view_args.clone(page=p))

		def sort_url(column, invert=False):
			desc = None
			if invert and not view_args.sort_desc:
				desc = 1
			return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

		actions, actions_confirmation = self.get_actions_list()
		deals = self.get_deals()

		clear_search_url = self._get_list_url(
			view_args.clone(page=0,
				 sort=view_args.sort,
				sort_desc=view_args.sort_desc,
				search=None,
				filters=None
			)
		)

		return self.render(self.list_template,
				data=data,
				# List
				list_columns=self._list_columns,
				sortable_columns=self._sortable_columns,
				# Stuff
				enumerate=enumerate,
				get_pk_value=self.get_pk_value,
				get_value=self.get_list_value,
				return_url=self._get_list_url(view_args),
				# Pagination
				count=count,
				pager_url=pager_url,
				num_pages=num_pages,
				page=view_args.page,
				# Sorting
				sort_column=view_args.sort,
				sort_desc=view_args.sort_desc,
				sort_url=sort_url,
				# Search
				search_supported=self._search_supported,
				clear_search_url=clear_search_url,
				search=view_args.search,
				# Filters
				filters=self._filters,
				filter_groups=self._filter_groups,
				active_filters=view_args.filters,
				# Actions
				actions=actions,
				actions_confirmation=actions_confirmation,
				#deals
				deals=deals)


from sqlalchemy.ext.declarative import DeclarativeMeta
def sa_obj_to_dict(obj, filtrate=None, rename=None):
	"""
	sqlalchemy 对象转为dict
	:param filtrate: 过滤的字段
	:type filtrate: list or tuple
	:param rename: 需要改名的,改名在过滤之后处理, key为原来对象的属性名称，value为需要更改名称
	:type rename: dict
	:rtype: dict
	"""

	if isinstance(obj.__class__, DeclarativeMeta):
		# an SQLAlchemy class
		#该类的相关类型，即直接与间接父类
		cla = obj.__class__.__mro__
		#过滤不需要的父类
		cla = filter(lambda c: hasattr(c, '__table__'), filter(lambda c: isinstance(c, DeclarativeMeta), cla))
		columns = []
		map(lambda c: columns.extend(c.__table__.columns), cla[::-1])
		# columns = obj.__table__.columns
		if filtrate and isinstance(filtrate, (list, tuple)):
			fields = dict(map(lambda c: (c.name, getattr(obj, c.name)), filter(lambda c: not c.name in filtrate, columns)))
		else:
			fields = dict(map(lambda c: (c.name, getattr(obj, c.name)), columns))
		# fields = dict([(c.name, getattr(obj, c.name)) for c in obj.__table__.columns])
		if rename and isinstance(rename, dict):
			#先移除key和value相同的项
			_rename = dict(filter(lambda (k, v): str(k) != str(v), rename.iteritems()))
			#如果原始key不存在，那么新的key对应的值默认为None
			#如果新的key已存在于原始key中，那么原始key的值将被新的key的值覆盖
			# map(lambda (k, v): fields.setdefault(v, fields.pop(k, None)), _rename.iteritems())
			map(lambda (k, v): fields.update({v: fields.pop(k, None)}), _rename.iteritems())
		#
		return fields
	else:
		return {}