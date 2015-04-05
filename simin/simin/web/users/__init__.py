# coding: utf-8
from flask import Blueprint
from flask.ext.login import LoginManager, current_user
from flask.ext.login import login_user, logout_user, login_required
from sqlalchemy.sql import or_
from simin.web.admin import SModelView
from simin.web.core import admin, sql, json_success, json_error
from simin.web.filters import auto_markup
from simin.utils import time2best
from .forms import *
from .models import *
from .views import *


class UserManager(object):

	def __init__(self, app=None, **options):
		self.setup(options)
		if app is not None:
			self.init_app(app)

	def setup(self, options):
		""" Setup Options """
		# Global Options
		self.set_option('sql',				options, sql)
		self.set_option('model', 			options, User)

		# Check Options
		self.set_option('check_view',		options, check_view)
		self.set_option('check_endpoint',	options, 'users.check')
		self.set_option('check_url',		options, '/users/check')

		# Register Options
		self.set_option('register_view',	options, register_view)
		self.set_option('register_endpoint',options, 'users.register')
		self.set_option('register_url',		options, '/users/register')
		self.set_option('register_next',	options, '/users/login')
		self.set_option('register_form',	options, RegisterForm)
		self.set_option('register_template',options, 'simin_user/register.html')

		# Login Options
		self.set_option('login_view', 		options, login_view)
		self.set_option('login_endpoint', 	options, 'users.login')
		self.set_option('login_url', 		options, '/users/login')
		self.set_option('login_next', 		options, '/')
		self.set_option('login_form',		options, LoginForm)
		self.set_option('login_template',	options, 'simin_user/login.html')

		# Logout Options
		self.set_option('logout_view',		options, logout_view)
		self.set_option('logout_endpoint',	options, 'users.logout')
		self.set_option('logout_url',		options, '/users/logout')
		self.set_option('logout_next',		options, '/users/login')

		# Forget Password Options
		self.set_option('forget_password_view',		options, forget_password_view)
		self.set_option('forget_password_endpoint',	options, 'users.forget_password')
		self.set_option('forget_password_url',		options, '/users/forget_password')
		self.set_option('forget_password_next',		options, '/users/login')
		self.set_option('forget_password_form',		options, ForgetPasswordForm)
		self.set_option('forget_password_template',	options, 'simin_user/forget_password.html')

		# Reset Password Options
		self.set_option('reset_password_view',		options, reset_password_view)
		self.set_option('reset_password_endpoint',	options, 'users.reset_password')
		self.set_option('reset_password_url',		options, '/users/reset_password')
		self.set_option('reset_password_next',		options, '/users/login')
		self.set_option('reset_password_form',		options, ResetPasswordForm)
		self.set_option('reset_password_form',		options, 'simin_user/reset_password.html')

	def set_option(self, attr, options, default=None):
		setattr(self, attr, options.get(attr, default))

	def init_app(self, app):
		app.user_manager = self
		self.init_login(app)
		self.init_routes(app)
		self.init_admin()

	def init_login(self, app):
		login_manager = LoginManager(app)
		login_manager.login_view = self.login_endpoint

		# User Loader
		@login_manager.user_loader
		def load_user(id):
			return self.get_user(id)

	def init_routes(self, app):
		app.add_url_rule(self.check_url, self.check_endpoint,
			self.check_view)
		app.add_url_rule(self.register_url, self.register_endpoint, 
			self.register_view, methods=['GET', 'POST'])
		app.add_url_rule(self.login_url, self.login_endpoint, 
			self.login_view, methods=['GET', 'POST'])
		app.add_url_rule(self.logout_url, self.logout_endpoint,
			self.logout_view)
		app.add_url_rule(self.forget_password_url, self.forget_password_endpoint,
			self.forget_password_view, methods=['GET', 'POST'])
		app.add_url_rule(self.reset_password_url, self.reset_password_endpoint,
			self.reset_password_view, methods=['GET', 'POST'])

	def init_admin(self):
		class UserView(SModelView):
			column_list = ('id', 'username', 'email', 'phone', 'regip', 'role', 'created')
			column_sortable_list = ('id', 'username', 'email', 'phone', 'regip', 'role', 'created')
			column_searchable_list = ('username', 'email', 'phone')

			def format_time(view, context, model, name):
				return auto_markup(time2best(model.created))

			def format_role(view, context, model, name):
				return auto_markup(model.format_role())
		
			column_formatters = {
				'role': format_role,
				'created': format_time,
			}

		admin.add_view(
			UserView(
				self.model,
				self.sql.session,
				name='users',
				endpoint='users.admin',
				url='/admin/users/',
			)
		)

	def check(self, args):
		username = args.get('username')
		if username is not None:
			if self.model.query.filter_by(username=username).count() > 0:
				return json_error(msg=u'用户名已经被注册')
			return json_success()

		email = args.get('email')
		if email is not None:
			if self.model.query.filter_by(email=email).count() > 0:
				return json_error(msg=u'邮箱已经被注册')
			return json_success()

		return json_error(msg=u'参数无效')

	def get_account(self, id):
		query = or_(
			self.model.username == id,
			self.model.email == id,
			self.model.phone == id,
		)
		return self.model.query.filter(query).first()

	def get_user(self, id=None, username=None, email=None, phone=None):
		if id is not None:
			return self.model.query.get(id)
		if username is not None:
			return self.model.query.filter_by(username=username).first()
		if email is not None:
			return self.model.query.filter_by(email=email).first()
		if phone is not None:
			return self.model.query.filter_by(phone=phone).first()

	def is_login(self):
		return current_user.is_authenticated()

	def login_user(self, form):
		user = form.get_user()
		if user is not None:
			login_user(user, form.remember.data)

	def logout_user(self):
		return logout_user()

	def register_user(self, form):
		return form.register(self.model)

	def forget_password(self, form):
		return form.forget_password(self.model)

	def reset_password(self, form):
		return form.reset_password(self.model)