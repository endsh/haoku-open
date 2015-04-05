#coding: utf-8
from __future__ import unicode_literals
from flask import current_app
from simin.web.forms import Form, VerifyCodeField
from wtforms.fields.html5 import EmailField
from wtforms import BooleanField, HiddenField, PasswordField, SubmitField, StringField,	validators, ValidationError, TextField
from wtforms.validators import Email, Regexp
from .validators import Strip, Lower, DataRequired, Length


def unique_username_validator(form, field):
	kuser_manager = current_app.kuser_manager
	if not kuser_manager.username_is_available(field.data):
		raise ValidationError("This username is already in use, Please try another one")

def unique_email_validator(form, field):
	kuser_manager = current_app.kuser_manager
	if not kuser_manager.email_is_available(field.data):
		raise ValidationError(_('This Email is already in use. Please try another one.'))

class ForgotPasswordForm(Form):
	email = EmailField(
		'邮箱地址', 
		validators=[
			Strip(), 
			Lower(), 
			DataRequired(), 
			Email(message='邮箱格式不正确'),
		]
	)

class ResendConfirmEmailForm(Form):
	email = TextField('邮箱地址')
	verify_code = VerifyCodeField('验证码', key='find_pass')


class ChangeUsernameForm(Form):
	username = TextField('用户名', validators=[
		unique_username_validator
	])
	verify_code = VerifyCodeField('验证码', key='find_pass')


class LoginForm(Form):
	username= TextField(
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

class ChangePasswordForm(Form):
	oldpassword = PasswordField(u'旧密码',  
		validators=[
			DataRequired(),
			Length(min=6, max=18),
			Regexp(
				r"""^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$""", 
				message='密码只能包含英文字符，数字或其他可见符号'
			),
		],)
	password = PasswordField(u'新密码', 
		validators=[
			DataRequired(),
			Length(min=6, max=18),
			Regexp(
				r"""^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$""", 
				message='密码只能包含英文字符，数字或其他可见符号'
			),
		],)
	repassword = PasswordField(u'确认密码', 
		validators=[
			DataRequired(),	],
		)
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
			unique_username_validator,
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
			unique_email_validator,
		]
	)