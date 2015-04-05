# coding: utf-8
from simin.web.core import sql, SessionMixin
from sqlalchemy_utils import PasswordType


class Account(sql.Model, SessionMixin):

	id = sql.Column(sql.Integer(), primary_key=True)
	active = sql.Column(sql.Boolean(), default=False)
	username = sql.Column(sql.String(40), unique=True)
	password = sql.Column(
		PasswordType(
			schemes=['pbkdf2_sha512', 'md5_crypt'],
			deprecated=['md5_crypt'],
		)
	)
	email = sql.Column(sql.String(40), unique=True)
	qq = sql.Column(sql.String(20), unique=True)
	weibo = sql.Column(sql.String(40), unique=True)
	douban = sql.Column(sql.String(40), unique=True)
	renren = sql.Column(sql.String(40), unique=True)
	weixin = sql.Column(sql.String(40), unique=True)
	phone = sql.Column(sql.String(40))
	access_token = sql.Column(sql.String(40), default='')
	reset_token = sql.Column(sql.String(40), default='')
	created = sql.Column(sql.Integer())

	def __repr__(self):
		return u'<Account {0}-{1}>'.format(self.username, self.email)
