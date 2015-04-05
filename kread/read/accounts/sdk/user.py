# coding: utf-8
from flask import current_app
from .apps import is_app, is_client, is_service
from .contant import *


class AnonymousUser(object):

	def __init__(self, appid=None, code=ACCESS_DENIED):
		self.appid = appid
		self.code = code

	def is_app(self):
		return is_app(self.appid)

	def is_client(self):
		return is_client(self.appid)

	def is_service(self):
		return is_service(self.appid)

	def access(self):
		abort(self.code)

	def access_client(self):
		abort(self.code)

	def access_service(self):
		abort(self.code)

	def access_user(self):
		abort(self.code)

	def public_access(self):
		if not self.is_app():
			abort(self.code)

	@property
	def args(self):
		args = {'appid':current_app.config.get('APPID')}
		return args


class User(AnonymousUser):

	def __init__(self, appid, uid):
		super(User, self).__init__(appid)
		self.uid = uid

	def access(self):
		pass

	def access_client(self):
		if not self.is_client():
			abort(self.code)

	def access_service(self):
		if not self.is_service():
			abort(self.code)

	def access_user(self):
		if not self.uid:
			abort(self.code)

	def public_access(self):
		pass

	@property
	def args(self):
		args = {
			'appid': current_app.config.get('APPID'),
			'uid': self.uid,
		}
		return args