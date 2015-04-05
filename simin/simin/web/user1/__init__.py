# coding: utf-8
import os
from flask import Blueprint, current_app
from flask.ext.login import LoginManager, current_user
from . import forms
from . import views
from . import settings

folder = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(folder, 'templates')


def _flask_user_context_processor():
	""" Make 'kuser_manager' available to Jinja2 templates"""
	return dict(user_manager=current_app.kuser_manager)


class KUserManager(object):

	def __init__(self, db, UserModel, app=None,
			# Forms 
			change_password_form=forms.ChangePasswordForm,
			change_username_form=forms.ChangeUsernameForm,
				
			login_form = forms.LoginForm,
			register_form=forms.RegisterForm,
			forgot_password_form=forms.ForgotPasswordForm,
			resend_confirm_email_form=forms.ResendConfirmEmailForm,
			# View function
			change_password_view_function=views.change_password,
			change_username_view_function=views.change_username,
				
			confirm_email_view_function=views.confirm_email,
			login_view_function=views.login,
			logout_view_function=views.logout,
			register_view_function=views.register,
			forgot_password_view_function=views.forgot_password,
			resend_confirm_email_view_function = views.resend_confirm_email,
			user_profile_view_function = views.user_profile,

			# other
			login_manager=LoginManager()):
		self.db = db
		self.UserModel = UserModel
		# forms
		self.change_password_form = change_password_form
		self.change_username_form = change_username_form
		self.login_form = login_form
		self.register_form = register_form
		self.forgot_password_form = forgot_password_form
		self.resend_confirm_email_form = resend_confirm_email_form
		# views functions
		self.change_password_view_function = change_password_view_function
		self.change_username_view_function = change_username_view_function
		self.login_view_function = login_view_function
		self.register_view_function = register_view_function
		self.forgot_password_view_function = forgot_password_view_function
		self.logout_view_function = logout_view_function
		self.confirm_email_view_function = confirm_email_view_function
		self.resend_confirm_email_view_function = resend_confirm_email_view_function
		self.user_profile_view_function = user_profile_view_function
		# other
		self.login_manager = login_manager

		if app is not None:
			self.init_app(app)

	def init_app(self, app):
		app.kuser_manager = self
		# set default settings.
		settings.set_default_settings(self, app.config)

		# setup flask-login
		self.setup_login_manager(app)

		# Add flask_user/templates directory using a Blueprint
		blueprint = Blueprint('user', 'user', template_folder=template_folder)
		app.register_blueprint(blueprint)

		# Add URL routes
		self.add_url_routes(app)

		# Add context processor
		app.context_processor(_flask_user_context_processor)

	def setup_login_manager(self, app):
		@self.login_manager.user_loader
		def load_user_by_id(user_unicode_id):
			user_id = int(user_unicode_id)
			return self.get_user_by_id(user_id)

		self.login_manager.login_view = self.login_endpoint
		self.login_manager.init_app(app)

	def add_url_routes(self, app):
		app.add_url_rule('/home',  'user.home',  self.login_view_function,  methods=['GET', 'POST'])
		app.add_url_rule(self.login_url,  'user.login',  self.login_view_function,  methods=['GET', 'POST'])
		app.add_url_rule(self.logout_url, 'user.logout', self.logout_view_function, methods=['GET', 'POST'])
		if self.enable_confirm_email:
			app.add_url_rule(self.confirm_email_url, 'user.confirm_email', self.confirm_email_view_function)
			app.add_url_rule(self.resend_confirm_email_url, 'user.resend_confirm_email', self.resend_confirm_email_view_function, methods=['GET', 'POST'])
		if self.enable_change_password:
			app.add_url_rule(self.change_password_url, 'user.change_password', self.change_password_view_function, methods=['GET', 'POST'])
		if self.enable_change_username:
			app.add_url_rule(self.change_username_url, 'user.change_username', self.change_username_view_function, methods=['GET', 'POST'])
		if self.enable_forgot_password:
			app.add_url_rule(self.forgot_password_url, 'user.forgot_password', self.forgot_password_view_function, methods=['GET', 'POST'])
			# app.add_url_rule(self.reset_password_url, 'user.reset_password', self.reset_password_view_function, methods=['GET', 'POST'])
		if self.enable_register:
			app.add_url_rule(self.register_url, 'user.register', self.register_view_function, methods=['GET', 'POST'])

		app.add_url_rule(self.user_profile_url,  'user.profile',  self.user_profile_view_function,  methods=['GET', 'POST'])


	def get_user_by_id(self, user_id):
		return self.UserModel.query.get(user_id)

	def find_user_by_username(self, username):
		if hasattr(self.UserModel, 'username'):
			return self.UserModel.query.filter_by(username=username).first()
		return None

	def find_user_by_email(self, email):
		if hasattr(self.UserModel, 'email'):
			return self.UserModel.query.filter_by(email=email).first()
		return None

	def username_is_available(self, new_username):
		return self.find_user_by_username(new_username) == None

	def email_is_available(self, email):
		user = self.find_user_by_email(email)
		if hasattr(user, 'active'):
			return user == None and user.active
		return user == None

	def add_user(self, **kwargs):
		object = UserModel(**kwargs)
		self.db.session.add(object)
		return object
		
	def commit(self):
		self.db.session.commit()