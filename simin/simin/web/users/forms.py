# coding: utf-8
from __future__ import unicode_literals
import time
from flask import current_app, request
from wtforms import BooleanField, PasswordField, TextField
from wtforms.fields.html5 import EmailField
from simin.web.forms import Form, VerifyCodeField
from simin.web.forms import Strip, Lower, Length, DataRequired
from simin.web.forms import Email, Regexp
#from .email import create_code, send_reset_password_email


class LoginForm(Form):
	account = TextField(
		'用户名、邮箱或手机',
		validators=[
			Strip(),
			Lower(),
			DataRequired(),
		],
	)
	password = PasswordField(
		'密码',
		validators=[
			DataRequired(),
		],
	)
	remember = BooleanField('记住我一个月')
	verify_code = VerifyCodeField('验证码', key='user_login')

	def validate_account(self, field):
		um = current_app.user_manager
		user = um.get_account(self.account.data)
		if user is None:
			raise ValueError('帐号不存在')
		if user.password != self.password.data:
			raise ValueError('密码不正确')
		self.user = user

	def get_user(self):
		if hasattr(self, 'user'):
			return self.user


class RegisterForm(Form):
	username = TextField(
		'用户名',
		validators=[
			Strip(),
			Lower(),
			DataRequired(),
			Length(min=6, max=18),
			Regexp(
				r'^[\w\d]+[\d\w_]+$', 
				message='用户名只能包含英文字符，数字或下划线'
			),
		],
	)
	password = PasswordField(
		'密码',
		validators=[
			DataRequired(),
			Length(min=6, max=18),
			Regexp(
				r"""^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$""", 
				message='密码只能包含英文字符，数字或其他可见符号'
			),
		],
	)
	re_password = PasswordField(
		'确认密码',
		validators=[
			DataRequired(),
		],
	)
	email = EmailField(
		'邮箱地址',
		validators=[
			Strip(),
			Lower(),
			DataRequired(),
			Email(message='邮箱格式不正确'),
		]
	)
	verify_code = VerifyCodeField('验证码', key='user_register')

	def validate_re_password(self, field):
		if password.data != re_password.data:
			raise ValueError(u'两次密码不一样')

	def register(self, model):
		user = model(
			username=self.username.data, 
			password=self.password.data,
			email=self.email.data,
			regip=request.remote_addr,
			created=time.time(),
		)
		user.save()
		return user


class ForgetPasswordForm(Form):
	email = EmailField(
		'邮箱地址',
		validators=[
			Strip(),
			Lower(),
			DataRequired(),
			Email(message='邮箱格式不正确'),
		]
	)
	verify_code = VerifyCodeField('验证码', key='user_forget_password')

	def validate_email(self, field):
		user = current_app.user_manager.get_user(email.data)
		if user is None:
			raise ValueError(u'该邮箱不存在。')
		self.user = user

	def forget_password(self, model):
		if hasattr(self, 'user'):
			self.user.reset_email_code = create_code(user)
			return send_reset_password_email(user)
		return False


class ResetPasswordForm(Form):
	password = PasswordField(
		'新密码',
		validators=[
			DataRequired(),
			Length(min=6, max=18),
			Regexp(
				r"""^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$""", 
				message='密码只能包含英文字符，数字或其他可见符号'
			),
		],
	)
	re_password = PasswordField(
		'确认密码',
		validators=[
			DataRequired(),
		],
	)

	def validate_re_password(self, field):
		if password.data != re_password.data:
			raise ValueError(u'两次密码不一样')

	def reset_password(self, model):
		pass