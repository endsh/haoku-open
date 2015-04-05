# coding: utf-8
from simin.web.forms import Form, VerifyCodeField
from simin.web.forms import KDateField, KRadioField
from wtforms import fields


class ProfileForm(Form):
	nickname = fields.TextField(u'昵称')
	birthday = KDateField(u'生日', allow_null=True)
	sex = KRadioField(u'性别', choices=[('male',u'男'), ('female',u'女')])
	city = fields.TextField(u'所在城市')
	site = fields.TextField(u'个人主页')
	signature = fields.TextField(u'个性签名')
	intro = fields.TextField(u'个人介绍')
	

class AvatarForm(Form):
	avatar = fields.FileField(u'上传头像')


class ChangePasswordForm(Form):
	oldpassword = fields.PasswordField(u'旧密码')
	password = fields.PasswordField(u'新密码')
	repassword = fields.PasswordField(u'确认密码')