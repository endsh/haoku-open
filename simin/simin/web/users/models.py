# coding: utf-8
from simin.web.core import sql, SessionMixin
from sqlalchemy_utils import PasswordType


class User(sql.Model, SessionMixin):
	ROLE_UNACTIVE = 0
	ROLE_COMMON = 1
	ROLE_ADMIN = 2
	ROLE_SUPER = 3

	ROLES = {
		ROLE_UNACTIVE: u'未激活',
		ROLE_COMMON: u'普通用户',
		ROLE_ADMIN: u'管理员',
		ROLE_SUPER: u'超级管理员',
	}

	id = sql.Column(sql.Integer(), primary_key=True)
	username = sql.Column(sql.String(40), unique=True)
	password = sql.Column(
		PasswordType(
			schemes=['pbkdf2_sha512', 'md5_crypt'],
			deprecated=['md5_crypt'],
		)
	)
	role = sql.Column(sql.Integer(), default=ROLE_UNACTIVE)
	email = sql.Column(sql.String(40), unique=True)
	phone = sql.Column(sql.String(40), unique=True)
	weibo = sql.Column(sql.String(40), unique=True)
	weixin = sql.Column(sql.String(40), unique=True)
	renren = sql.Column(sql.String(40), unique=True)
	douban = sql.Column(sql.String(40), unique=True)
	access_email_code = sql.Column(sql.String(40), default='')
	access_phone_code = sql.Column(sql.String(40), default='')
	reset_email_code = sql.Column(sql.String(40), default='')
	reset_phone_code = sql.Column(sql.String(40), default='')
	regip = sql.Column(sql.String(20))
	created = sql.Column(sql.Integer())

	def format_role(self):
		return User.ROLES[self.role]

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	def __repr__(self):
		return u'<User {0} - {1}>'.format(self.username, self.id)
