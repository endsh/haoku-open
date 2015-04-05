# coding: utf-8
import time
import hashlib
from flask.ext.admin.form import rules
from flask.ext.admin.base import expose
from flask.ext.admin.contrib.pymongo import filters
from flask.ext.login import current_user
from flask import request, redirect, current_app
from utils import time2best
from .base import ModelView, SqlModelsView
from .deals import deal
from .forms import DomainForm, DomainEditForm, CateForm
from .forms import TplForm, TplEditForm, ArtForm, RecodeForm, TaskForm
from .forms import RoleForm, UserForm
from ..core import admin, mongo_iweb, mongo_admin, db
from ..filters import auto_markup
from flask.ext.admin.contrib import sqla
from ..account.models import Account, Role
# 

class DomainView(ModelView):
	column_list = ('_id', 'name', 'cates', 'tpls', 'arts', 'last')
	column_sortable_list = ('_id', 'name', 'cates', 'tpls', 'arts', 'last')

	column_searchable_list = ('_id', 'name', )
	
	form = DomainForm

	def get_edit_form(self):
		return DomainEditForm

	def format_time(view, context, model, name):
		return auto_markup(time2best(model['last']))
		
	column_formatters = {
		'last': format_time,
	}

	edit_form_widget_args = {
		'_id':{
			'disabled' : True
		}
	}


class CateView(ModelView):
	column_list = ('url', 'name', 'domain', 'arts', 'fetch', 'null', 'error', 'last')
	column_sortable_list = ('url', 'domain', 'name', 'arts', 'fetch', 'null', 'error', 'last')
	column_searchable_list = ('name', 'url')
	form = CateForm
	edit_form_widget_args = {
		'url':{
			'disabled' : True
		}
	}

	def format_time(view, context, model, name):
		return auto_markup(time2best(model['last']))

	column_formatters = {
		'last': format_time,
	}


class TplView(ModelView):
	column_list = ('_id', 'domain', 'arts')
	column_sortable_list = ('_id', 'domain', 'arts')
	column_searchable_list = ('_id', 'arts')
	form = TplForm

	edit_form_widget_args = {
		'_id':{
			'disabled' : True
		}
	}

	def get_edit_form(self):
		return TplEditForm

class ArtView(ModelView):
	column_list = ('url', 'title', 'src_name', 'pubtime')
	column_sortable_list = ('url', 'title', 'src_name', 'pubtime')

	form = ArtForm

	edit_form_widget_args = {
		'url':{
			'disabled' : True
		}
	}

	def url_formatter(view, context, model, name):
		if 'url' not in model or not model['url']:
			return ''
		line = '<a href="%s" title="%s" target="_blank">%s</a>'
		url = model.get('url', '')
		title = model.get('title', '')
		short = (url[:25] + '...') if len(url) > 28 else url 
		return auto_markup(line % (url, title, short))

	def format_time(view, context, model, name):
		return auto_markup(time2best(model['pubtime']))

	column_formatters = {
		'url': url_formatter,
		'pubtime': format_time,
	}

	@deal(u'正文', '/content/')
	def content_view(self):
		return u'正文'
		

class ArticleView(ModelView):
	column_list = ('url', 'tags', 'domain', 'src_name', 'pubtime')
	column_sortable_list = ('domain', 'src_name', 'pubtime')

	form = ArtForm

	edit_form_widget_args = {
		'url':{
			'disabled' : True
		}
	}

	def url_formatter(view, context, model, name):
		if 'url' not in model or not model['url']:
			return ''
		line = '<a href="%s" title="%s" target="_blank">%s</a>'
		base = current_app.config.get('WEB_TEST_URL')
		url = '%sa/%s/%s.html' % (base, model.get('id', '')[:8],  model.get('id', '')[8:])
		title = model.get('title', '')
		short = (title[:17] + '...') if len(title) > 20 else title
		return auto_markup(line % (url, title, short))

	def tags_formatter(view, context, model, name):
		if 'tags' not in model or not model['tags']:
			return ''

		line = '<a href="%s" title="%s" target="_blank">%s</a>'
		base = current_app.config.get('WEB_TEST_URL')
		url = base + 'topics/%s' 
		tags = [line % (url % x, x, x) for x in model.get('tags', [])[:2]]
		return auto_markup(' | '.join(tags))

	def format_time(view, context, model, name):
		return auto_markup(time2best(model['pubtime']))

	column_formatters = {
		'url': url_formatter,
		'tags': tags_formatter,
		'pubtime': format_time,
	}

class RecodeView(ModelView):
	column_list = ('_id', 'title', 'content', 'task_title', 'pubtime')
	form = RecodeForm

	def get_list(self, *args, **kwargs):
		count, data = super(RecodeView, self).get_list(*args, **kwargs)
		query = {'_id': {'$in': [x['task_id'] for x in data]}}
		tasks = mongo_admin.task.find(query, {'title':1, '_id':0})
		# Contribute user names to the models
		tasks_map = dict((x['_id'], x['title']) for x in tasks)

		for item in data:
			item['task_title'] = tasks_map.get(str(item['task_id']))

		return count, data

	# Contribute list of user choices to the forms
	def _feed_role_choices(self, form, is_created=False):
		tasks = mongo_admin.task.find({'user_id':str(current_user.id)})
		form.task_id.choices = [(str(x['_id']), x['title']) for x in tasks]
		return form

	def create_form(self):
		form = super(RecodeView, self).create_form()
		return self._feed_role_choices(form)

	def edit_form(self, obj):
		form = super(RecodeView, self).edit_form(obj)
		return self._feed_role_choices(form)


class TaskView(ModelView):
	column_list = ('_id', 'title', 'content', 'user_name', 'pubtime')

	form = TaskForm	

	def get_list(self, *args, **kwargs):
		count, data = super(TaskView, self).get_list(*args, **kwargs)
		users = Account.query.all()
		users_map = dict((x.id, x.username) for x in users)

		for item in data:
			print users_map, item['user_id']
			try:

				item['user_name'] = users_map.get(int(item['user_id']), item['user_id'])
			except Exception, e:
				print e
				item['user_name'] = item['user_id']
		return count, data

	# Contribute list of user choices to the forms
	def _feed_role_choices(self, form, is_created=False):
		users = Account.query.all()
		form.user_id.choices = [(str(x.id), x.username) for x in users]
		return form

	def create_form(self):
		form = super(TaskView, self).create_form()
		return self._feed_role_choices(form)

	def edit_form(self, obj):
		form = super(TaskView, self).edit_form(obj)
		return self._feed_role_choices(form)

from sqlalchemy_utils import PasswordType

class UserAdmin(SqlModelsView):
	column_list = ('id', 'username', 'phone', 'email_verify')
	DEFAULT_PASSWORD = '888888'

	def on_model_change(self, form, model, is_created=None):
		if is_created:
			model.password = self.DEFAULT_PASSWORD


def register_mongo_admin(app):
	admin.add_view(
		DomainView(
			coll=mongo_iweb.domain, 
			name=u'网站', 
			endpoint='domain', 
			url='/mongo/domain',
		)
	)
	admin.add_view(
		CateView(
			coll=mongo_iweb.catecory,
			name=u'分类',
			endpoint='catecory',
			url='/mongo/catecory',
		)
	)
	admin.add_view(
		TplView(
			coll=mongo_iweb.template,
			name=u'模板',
			endpoint='template',
			url='/mongo/template',
		)
	)
	admin.add_view(
		ArtView(
			coll=mongo_iweb.spider_article,
			name=u'文章',
			endpoint='article',
			url='/mongo/article',
		)
	)
	admin.add_view(
		ArticleView(
			coll=mongo_iweb.article,
			name=u'Web文章',
			endpoint='web_article',
			url='/mongo/web_article',
		)
	)
	admin.add_view(
		UserAdmin(
			Account,
			db.session,
			name=u'User',
			endpoint='user',
			url='/accounts/user',
		)
	)
	admin.add_view(
		SqlModelsView(
			Role,
			db.session,
			name=u'Role',
			endpoint='role',
			url='/accounts/role',
		)
	)
	admin.add_view(TaskView(
			coll=mongo_admin.task,
			name=u'Task',
			endpoint='task',
			url='/journal/task',
		)
	)
	admin.add_view(RecodeView(
			coll=mongo_admin.recode,
			name=u'Recode',
			endpoint='recode',
			url='/journal/recode',
		)
	)