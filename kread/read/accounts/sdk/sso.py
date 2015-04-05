# coding: utf-8
import time
import urllib
import json
from datetime import timedelta, datetime
from flask import Blueprint, render_template, redirect, url_for
from flask import has_request_context, _request_ctx_stack
from flask import request, session, jsonify, current_app
from werkzeug.local import LocalProxy
from werkzeug.security import safe_str_cmp
from accounts.sdk import settings
from utils import get_host
from .apps import *
from .contant import *
from .settings import SSO_TEMPLATE_FOLDER, ACCOUNTS_LOGIN

current_user = LocalProxy(lambda: _get_user())

COOKIE_NAME = 'remember_token'
COOKIE_DURATION = timedelta(days=30)
COOKIE_SECURE = None
COOKIE_HTTPONLY = False


class AnonymousUser(object):

	@property
	def login(self):
		return False

	@property
	def active(self):
		return False

	@property
	def args(self):
		args = {'appid':current_app.config.get('APPID')}
		return args


class User(object):

	def __init__(self, uid, username, avatar):
		self.uid = uid
		self.username = username
		self.avatar = avatar

	def _avatar(self, width=100):
		if current_app.status == 'DEBUG':
			return self.avatar
		return '%s@%dw_%dh_1c_1e_95Q.jpg' % (self.avatar, width, width)

	@property
	def avatar_small(self):
		return self._avatar(64)

	@property
	def avatar_normal(self):
		return self._avatar(100)

	@property
	def avatar_large(self):
		return self._avatar(120)

	@property
	def login(self):
		return True

	@property
	def active(self):
		return True

	@property
	def args(self):
		args = {
			'appid': current_app.config.get('APPID'),
			'uid': self.uid,
		}
		return args


class SSOManager(object):

	def __init__(self, app=None, access_url='/access', 
			jsonp_url='/jsonp', login_url='/login', logout_url='/logout'):
		self.access_url = access_url
		self.jsonp_url = jsonp_url
		self.login_url = login_url
		self.logout_url = logout_url
		self.urls = {}
		for attr in dir(settings):
			if attr.startswith('ACCOUNTS_') or attr.startswith('WEB_'):
				self.urls[attr] = getattr(settings, attr)

		self.bp = Blueprint('sso', __name__, template_folder=SSO_TEMPLATE_FOLDER)
		self._anonymous_user_callback = None
		self._user_callback = None

		if app is not None:
			self.init_app(app)

	@property
	def context(self):
		_context = dict(
			current_user=current_user,
		)
		_context.update(self.urls)
		return _context

	def init_app(self, app):
		app.sso = self
		self.appid = app.config.get('APPID', 0)

		@self.bp.route(self.login_url)
		def goto_login():
			next = request.args.get('next', '')
			if get_host(next) != request.host:
				return redirect('/')

			params = urllib.urlencode({'next':next.encode('utf-8')})
			url = '%s?%s' % (ACCOUNTS_LOGIN, params)
			return redirect(url)

		@self.bp.route(self.access_url)
		def access():
			return self.access()

		@self.bp.route(self.jsonp_url)
		def jsonp():
			return self.jsonp()

		@self.bp.route(self.logout_url)
		def logout():
			return self.logout()

		@app.context_processor
		def context_processor():
			return self.context

		app.register_blueprint(self.bp)
		app.after_request(self._update_remember_cookie)

	def jsonp(self):
		next = request.args.get('next') or '/'
		if get_host(next) != request.host:
			return ''

		return 'window.location.href="%s";' % next

	def access(self):
		token = request.args.get('token')
		remember = request.args.get('remember') == 'true'
		if not token:
			abort(INVALID_TOKEN)

		res = current_user.accounts.access(token=token)
		if res['code'] == 0:
			self.login(res['user'], token, remember=remember)
			return ''

		abort(INVALID_TOKEN, api_code=code)

	def logout(self):
		for x in ['uid', 'username', 'avatar', 'token', 'access_time']:
			session.pop(x, None)

		cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
		if cookie_name in request.cookies:
			session['remember'] = 'clear'

		self._load_user(access_token=False)
		return ''

	def login(self, user, token, remember=False):
		session['uid'] = user['uid']
		session['username'] = user['username']
		session['avatar'] = user['avatar']
		session['token'] = token
		session['access_time'] = time.time()
		if remember == True:
			session['remember'] = 'set'

	def _load_user(self, access_token=True):
		ctx = _request_ctx_stack.top

		uid = session.get('uid')
		if uid is None and access_token:
			self.access_token()

		uid = session.get('uid')
		username = session.get('username')
		avatar = session.get('avatar')

		if uid is None:
			ctx.user = self.anonymous_user()
		else:
			ctx.user = self.user(uid, username, avatar)

	def access_token(self):
		cookie_name = current_app.config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
		if cookie_name in request.cookies:
			token = request.cookies[cookie_name]
			if token:
				res = self.anonymous_user().accounts.access(token=token)
				if res['code'] == 0:
					self.login(res['user'], token)

	def anonymous_user_callback(self, callback):
		self._anonymous_user_callback = callback
		return callback

	def user_callback(self, callback):
		self._user_callback = callback
		return callback

	def anonymous_user(self):
		if self._anonymous_user_callback is not None:
			return self._anonymous_user_callback()
		return AnonymousUser()

	def user(self, uid, username, avatar):
		if self._user_callback is not None:
			return self._user_callback(uid, username, avatar)
		return User(uid, username, avatar)

	def setup_user(self, publics={}, privates={}):

		class KAnonymousUser(AnonymousUser):

			def __init__(self):
				super(KAnonymousUser, self).__init__()
				for name, cls in publics.iteritems():
					setattr(self, name, cls(self))


		class KUser(User):

			def __init__(self, uid, username, avatar):
				super(KUser, self).__init__(uid, username, avatar)
				for name, cls in publics.iteritems():
					setattr(self, name, cls(self))
				for name, cls in privates.iteritems():
					setattr(self, name, cls(self))

		@self.anonymous_user_callback
		def anonymous_user_callback():
			return KAnonymousUser()

		@self.user_callback
		def user_callback(uid, username, avatar):
			return KUser(uid, username, avatar)

	def _update_remember_cookie(self, response):
		if 'remember' in session:
			operation = session.pop('remember', None)

			if operation == 'set' and 'uid' in session:
				self._set_cookie(response)
			elif operation == 'clear':
				self._clear_cookie(response)

		return response

	def _set_cookie(self, response):
		config = current_app.config
		cookie_name = config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
		duration = config.get('REMEMBER_COOKIE_DURATION', COOKIE_DURATION)
		domain = config.get('REMEMBER_COOKIE_DOMAIN')
		secure = config.get('REMEMBER_COOKIE_SECURE', COOKIE_SECURE)
		httponly = config.get('REMEMBER_COOKIE_HTTPONLY', COOKIE_HTTPONLY)

		data = session.get('token')
		expires = datetime.utcnow() + duration
		response.set_cookie(cookie_name,
				value=data, 
				expires=expires, 
				domain=domain,
				secure=secure, 
				httponly=httponly)

	def _clear_cookie(self, response):
		config = current_app.config
		cookie_name = config.get('REMEMBER_COOKIE_NAME', COOKIE_NAME)
		domain = config.get('REMEMBER_COOKIE_DOMAIN')
		response.delete_cookie(cookie_name, domain=domain)


def login_required(func):
	def wrapper(*args, **kwargs):
		if not current_user.login:
			params = urllib.urlencode({'next':request.url.encode('utf-8')})
			url = '%s?%s' % (ACCOUNTS_LOGIN, params)
			return redirect(url)
		return func(*args, **kwargs)
	wrapper.__name__ = func.__name__
	return wrapper


def _get_user():
	if has_request_context() and \
			not hasattr(_request_ctx_stack.top, 'user'):
		current_app.sso._load_user()

	return getattr(_request_ctx_stack.top, 'user', None)