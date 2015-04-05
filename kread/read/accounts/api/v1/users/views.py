# coding: utf-8
import re
import time
from simin.web.api import strip
from flask import request, current_app
from flask.ext.restful import reqparse, Resource
from sqlalchemy.sql import or_
from .models import Account
from ..core import api, access
from ..common import send_reset_pass_email, create_access_token, decode_access_token
from ..contant import *
from ..image import avatar2url
from ..profile import Profile
from ..token import create_token

RES = dict(
	username=re.compile(r'^[\w\d]+[\d\w_]+$'),
	password=re.compile(r"""^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$"""),
	email=re.compile(r'^[\w\d]+[\d\w_.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$'),
)


@access.public
class Register(Resource):

	def __init__(self):
		super(Register, self).__init__()
		self.req = reqparse.RequestParser()
		self.req.add_argument('username', type=unicode, required=True)
		self.req.add_argument('password', type=unicode, required=True)
		self.req.add_argument('email', type=unicode)
		self.req.add_argument('phone', type=unicode)
		self.req.add_argument('qq', type=unicode)
		self.req.add_argument('weibo', type=unicode)
		self.req.add_argument('douban', type=unicode)
		self.req.add_argument('renren', type=unicode)
		self.req.add_argument('weixin', type=unicode)
		self.req.add_argument('code', type=unicode)
		self.req.add_argument('type', type=unicode, required=True)

	def post(self):
		args = strip(self.req.parse_args(), 'password')
		self.validate(args)
		if hasattr(self, 'from_%s' % args['type']):
			return getattr(self, 'from_%s' % args['type'])(args)
		abort(INVALID_ARGS)

	def validate(self, args):
		self.validate_username(args['username'])
		self.validate_password(args['password'])

	def validate_username(self, username):
		if not username:
			abort(USERNAME_NULL)

		username_len = len(username)
		if username_len < 6:
			abort(USERNAME_TOO_SHORT)
		elif username_len > 18:
			abort(USERNAME_TOO_LONG)
		elif not RES['username'].match(username):
			abort(USERNAME_FORMAT_ERROR)
		elif Account.query.filter_by(username=username).count() > 0:
			abort(USERNAME_EXISTS)

	def validate_password(self, password):
		if not password:
			abort(PASSWORD_NULL)

		password_len = len(password)
		if password_len < 6:
			abort(PASSWORD_TOO_SHORT)
		elif password_len > 18:
			abort(PASSWORD_TOO_LONG)
		elif not RES['password'].match(password):
			abort(PASSWORD_FORMAT_ERROR)

	def from_email(self, args):
		self.required(args, 'email')
		self.validate_email(args['email'])
		self.save(args, 'email', active=False)
		return {}

	def validate_email(self, email):
		if len(email) >= 40:
			abort(EMAIL_TOO_LONG)
		elif not RES['email'].match(email):
			abort(EMAIL_FORMAT_ERROR)
		elif Account.query.filter_by(email=email).count() > 0:
			abort(EMAIL_EXISTS)

	def from_phone(self, args):
		pass

	def from_qq(self, args):
		pass

	def from_weibo(self, args):
		pass

	def from_douban(self, args):
		pass

	def from_renren(self, args):
		pass

	def from_weixin(self, args):
		pass

	def required(self, args, key):
		if key not in args or args[key] is None:
			abort(ARGS_REQUIRED, key=key)

	def save(self, args, *keys, **exts):
		fields = dict(
			username=args['username'],
			password=args['password'],
		)
		fields.update(dict((x, args[x]) for x in keys))
		fields.update(exts)
		account = Account(**fields)
		account.save()


@access.public
class Login(Resource):

	def __init__(self):
		super(Login, self).__init__()
		self.req = reqparse.RequestParser()
		self.req.add_argument('account', type=unicode, required=True)
		self.req.add_argument('password', type=unicode, required=True)

	def post(self):
		args = strip(self.req.parse_args(), 'password')
		self.validate(args)

		query = or_(
			Account.username == args['account'], 
			Account.email == args['account'],
		)
		user = Account.query.filter(query).first()
		if user is not None:
			if user.password != args['password']:
				abort(PASSWORD_ERROR)
			else:
				default = current_app.config.get('DEFAULT_AVATAR')
				profile = Profile.query.get(user.id)
				avatar = profile.avatar if profile and profile.avatar else default
				return dict(
					user=dict(uid=user.id, username=user.username, avatar=avatar2url(avatar)),
					token=create_token(3001, user.id, user.password.hash, time.time()),
				)
		else:
			abort(ACCOUNT_NOT_EXISTS)

	def validate(self, args):
		if not args['account']:
			abort(ACCOUNT_NULL)
		if not args['password']:
			abort(PASSWORD_NULL)

	def validate_username(self, username):
		username_len = len(username)
		if username_len < 6:
			abort(USERNAME_TOO_SHORT)
		elif username_len > 18:
			abort(USERNAME_TOO_LONG)
		elif not RES['username'].match(username):
			abort(USERNAME_FORMAT_ERROR)
		elif Account.query.filter_by(username=username).count() > 0:
			abort(USERNAME_EXISTS)


@access.public
class Check(Resource):

	def get(self):
		username = request.args.get('username')
		if username is not None:
			return self.check_username(username)

		email = request.args.get('email')
		if email is not None:
			return self.check_email(email)

		abort(INVALID_ARGS)

	def check_username(self, username):
		if Account.query.filter_by(username=username).count() > 0:
			abort(USERNAME_EXISTS)
		return {}

	def check_email(self, email):
		if Account.query.filter_by(email=email).count() > 0:
			abort(EMAIL_EXISTS)
		return {}


@access.public
class ResetPass(Resource):

	def __init__(self):
		super(ResetPass, self).__init__()
		self.req = reqparse.RequestParser()
		self.req.add_argument('code', type=unicode, required=True)
		self.req.add_argument('password', type=unicode)
		self.req.add_argument('repassword', type=unicode)

	def get(self):
		email = request.args.get('email', '')
		if not RES['email'].match(email):
			abort(EMAIL_FORMAT_ERROR)

		user = Account.query.filter_by(email=email).first()
		if not user:
			abort(EMAIL_NOT_FOUND)

		user.reset_token, code = create_access_token(user.email, time.time())
		user.update()
		send_reset_pass_email(user, code)
		return {}

	def post(self):
		args = self.req.parse_args()
		email, t, key = decode_access_token(args['code'])
		user = Account.query.filter_by(email=email).first()
		time_limit = current_app.config.get('EMAIL_TOKEN_TIME_LIMIT')
		if not user or key != user.reset_token or time.time() - t > time_limit:
			abort(INVALID_URL)

		if args['password']:
			self.validate_password(args['password'])
			if args['password'] != args['repassword']:
				abort(REPASSWORD_DIFF)
			user.password = args['password']
			user.reset_token = 'already_reset'
			user.update()
		return {}

	def validate_password(self, password):
		if not password:
			abort(PASSWORD_NULL)

		password_len = len(password)
		if password_len < 6:
			abort(PASSWORD_TOO_SHORT)
		elif password_len > 18:
			abort(PASSWORD_TOO_LONG)
		elif not RES['password'].match(password):
			abort(PASSWORD_FORMAT_ERROR)


api.add_resource(Register, '/users/register')
api.add_resource(Login, '/users/login')
api.add_resource(Check, '/users/check')
api.add_resource(ResetPass, '/users/reset_pass')