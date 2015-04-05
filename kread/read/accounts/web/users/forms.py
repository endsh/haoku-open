# coding: utf-8
from simin.web.forms import Form, VerifyCodeField
from wtforms import fields


class RegisterForm(Form):
	username = fields.TextField(u'用户名')
	password = fields.PasswordField(u'密码')
	email = fields.TextField(u'邮箱地址')
	verify_code = VerifyCodeField(u'验证码', key='register')


class LoginForm(Form):
	account = fields.TextField(u'用户名或邮箱')
	password = fields.PasswordField(u'密码')
	verify_code = VerifyCodeField(u'验证码', key='login')
	rememberme = fields.BooleanField(u'记住我一个月')


class FindPassForm(Form):
	email = fields.TextField(u'邮箱地址')
	verify_code = VerifyCodeField(u'验证码', key='find_pass')


class ResetPassForm(Form):
	password = fields.PasswordField(u'新密码')
	repassword = fields.PasswordField(u'确认密码')