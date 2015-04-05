# coding: utf-8
import time
from flask import has_request_context, _request_ctx_stack
from flask import request, session, jsonify, current_app
from werkzeug.local import LocalProxy
from werkzeug.security import safe_str_cmp
from .apps import *
from .contant import *
from .user import AnonymousUser, User

current_user = LocalProxy(lambda: _get_user())


class AccessManager(object):

	def __init__(self, app=None, access_url='/access', time_url='/time'):
		self.access_url = access_url
		self.time_url = time_url
		self._anonymous_user_callback = None
		self._user_callback = None
		self._public = ['access', 'server_time']
		if app is not None:
			self.init_app(app)

	def init_app(self, app):
		app.access = self

		@app.route(self.access_url)
		def access():
			return self.access()

		@app.route(self.time_url)
		def server_time():
			return jsonify({'now':time.time()})

		@app.before_request
		def before_request():
			if request.endpoint in self._public:
				current_user.public_access()
			else:
				current_user.access()

	def access(self):
		token = request.args.get('token')
		if not token:
			abort(INVALID_TOKEN)

		user, code = current_user.accounts.access(token=token)
		if code == 0:
			return self.login(user, token)
		abort(INVALID_TOKEN, api_code=code)

	def login(self, user, token):
		session['uid'] = user['uid']
		session['token'] = token
		session['access_time'] = time.time()
		session['access_key'] = self.access_key()
		return {'access_key': session['access_key']}

	def access_key(self):
		return os.urandom(16).encode('hex')

	def public(self, func=None, endpoint=None):
		if endpoint is None:
			endpoint = func.__name__.lower()
		self._public.append(endpoint)
		return func

	def load_user(self):
		ctx = _request_ctx_stack.top

		uid = session.get('uid')
		if uid is None:
			appid, uid, code = self.access_service()
			if appid is None:
				appid, code = self.public_access()
				ctx.user = self.anonymous_user(appid, code)
			else:
				ctx.user = self.user(appid, uid)
		else:
			self.access_time()
			appid, code = self.access_client()
			if appid is None:
				ctx.user = self.anonymous_user(appid, code)
			else:
				ctx.user = self.user(appid, uid)

	def access_time(self):
		t = session.get('access_time')
		if abs(time.time() - t) > 10800:
			token = session.get('token')
			user, code = self.decode(token)
			if code != 0:
				abort(INVALID_TOKEN_WITH_ACCESS_TIME, api_code=code)

			session['access_time'] = time.time()

	def access_service(self):
		appid = request.args.get('appid', 0, int)
		if not is_service(appid):
			return None, None, INVALID_SERVICE_ID

		t = request.args.get('t', 0, float)
		if abs(time.time() - t) > 60:
			return None, None, ACCESS_TIMEOUT

		sn = request.args.get('sn')
		if not sn or not safe_str_cmp(sn, sncode(request.args)):
			return None, None, ACCESS_DENIED

		return appid, request.args.get('uid', 0, int), 0

	def access_client(self):
		appid = request.args.get('appid', 0, int)
		if not is_client(appid):
			return None, INVALID_CLIENT_ID

		t = request.args.get('t', 0, float)
		if abs(time.time() - t) > 60:
			return None, ACCESS_TIMEOUT

		sn = request.args.get('sn')
		access_key = session.get('access_key')
		if not sn or not access_key \
				or not safe_str_cmp(sn, sncode(request.args, key=access_key)):
			return None, ACCESS_DENIED
		return appid, 0

	def public_access(self):
		appid = request.args.get('appid', 0, int)
		if not is_app(appid):
			return None, INVALID_CLIENT_ID

		t = request.args.get('t', 0, float)
		if abs(time.time() - t) > 86400:
			return None, INVALID_CLIENT_TIME

		sn = request.args.get('sn')
		if not sn or not safe_str_cmp(sn, sncode(request.args)):
			return None, ACCESS_DENIED

		return appid, 0

	def anonymous_user_callback(self, callback):
		self._anonymous_user_callback = callback
		return callback

	def user_callback(self, callback):
		self._user_callback = callback
		return callback

	def anonymous_user(self, appid, code):
		if self._anonymous_user_callback is not None:
			return self._anonymous_user_callback(appid, code)
		return AnonymousUser(code)

	def user(self, appid, uid):
		if self._user_callback is not None:
			return self._user_callback(appid, uid)
		return User(appid, uid)

	def setup_user(self, publics, privates):

		class KAnonymousUser(AnonymousUser):

			def __init__(self, appid=None, code=ACCESS_DENIED):
				super(KAnonymousUser, self).__init__(appid, code)
				for name, cls in publics.iteritems():
					setattr(self, name, cls(self))

		class KUser(User):

			def __init__(self, appid, uid):
				super(KUser, self).__init__(appid, uid)
				for name, cls in publics.iteritems():
					setattr(self, name, cls(self))
				for name, cls in privates.iteritems():
					setattr(self, name, cls(self))

		@self.anonymous_user_callback
		def anonymous_user_callback(appid, code):
			return KAnonymousUser(appid, code)

		@self.user_callback
		def user_callback(appid, uid):
			return KUser(appid, uid)


def _get_user():
	if has_request_context() and \
			not hasattr(_request_ctx_stack.top, 'user'):
		current_app.access.load_user()
	return getattr(_request_ctx_stack.top, 'user', None)


def access_client(func):
	def wrapper(*args, **kwargs):
		current_user.access_app()
		return func(*args, **kwargs)
	wrapper.__name__ = func.__name__
	return wrapper


def access_service(func):
	def wrapper(*args, **kwargs):
		current_user.access_service()
		return func(*args, **kwargs)
	wrapper.__name__ = func.__name__
	return wrapper