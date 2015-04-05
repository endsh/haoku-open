# coding: utf-8
from __future__ import unicode_literals
from wtforms import TextField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, Regexp
from .models import Account
from ..core import db
from ..kforms.forms import Form
from ..kforms.validators import Strip, Lower, DataRequired, Length


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
	repassword = PasswordField(
		'确认密码', validators=[DataRequired()],
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

	def validate_username(self, field):
		if Account.query.filter_by(username=field.data).count():
			raise ValueError('用户名已经被注册')

	def validate_repassword(self, field):
		if field.data != self.password.data:
			raise ValueError('两次密码不一致')

	def validate_email(self, field):
		if Account.query.filter_by(email=field.data).count():
			raise ValueError('邮箱已经被注册')

	def save(self, role=None):
		user = Account()
		self.populate_obj(user)
		if role:
			user.role = role
		user.save()
		return user


class LoginForm(Form):
	username_or_email = TextField(
		'用户名或邮箱', 
		validators=[
			Strip(),
			Lower(),
			DataRequired(),
		],
	)
	password = PasswordField(
		'密码', validators=[DataRequired()],
	)
	rememberme = BooleanField('记住我一个月')

	def validate_username_or_email(self, field):
		user = self.get_user()
		if user is None or user.password != self.password.data:
			raise ValueError('用户名不存在或密码不正确')

	def get_user(self):
		data = self.username_or_email.data
		return Account.query.filter(
			db.or_(
				Account.username == data,
				Account.email == data,
			)
		).first()
