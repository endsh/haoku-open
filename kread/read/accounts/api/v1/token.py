# coding: utf-8
import time
import base64
import hashlib
from flask import current_app
from flask.ext.restful import Resource
from accounts.sdk.apps import app_key
from .users import Account
from .core import api
from .access import current_user


class Token(Resource):

	def get(self):
		current_user.access_user()
		return create_tokens(current_user.uid)


class SSOToken(Resource):

	def get(self):
		current_user.access_service()
		current_user.access_user()
		return create_sso_tokens(current_user.uid)


class SSOLogout(Resource):

	def get(self):
		current_user.access_service()
		hosts = current_app.config.get('SSO_LOGOUT_HOSTS').values()
		return dict(hosts=hosts)


def create_token(appid, uid, password, t):
	key = app_key(appid)
	hsh = hashlib.md5(password).hexdigest()
	ostr = '|'.join(str(x) for x in [appid, key, uid, hsh, t])
	hsh = hashlib.md5(ostr.encode('utf-8')).hexdigest()
	return base64.b64encode('|'.join([str(uid), str(t), hsh]))


def create_tokens(uid):
	user = Account.query.get(uid)
	if user is None:
		abort(SERVER_ERROR)

	t = time.time()
	hosts = current_app.config.get('API_HOSTS')
	lab = lambda x: create_token(x, uid, user.password.hash, t)
	tokens = dict((y, lab(x)) for x, y in hosts.iteritems())
	return {'tokens': tokens}


def create_sso_tokens(uid):
	user = Account.query.get(uid)
	if user is None:
		abort(SERVER_ERROR)

	t = time.time()
	hosts = current_app.config.get('SSO_HOSTS')
	lab = lambda x: create_token(x, uid, user.password.hash, t)
	tokens = dict((y, lab(x)) for x, y in hosts.iteritems())
	return {'tokens': tokens}


api.add_resource(Token, '/token')
api.add_resource(SSOToken, '/ssotoken')
api.add_resource(SSOLogout, '/ssologout')