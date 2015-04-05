# coding: utf-8
import re
import time
import base64
from simin.web.api import strip
from flask import current_app
from flask.ext.restful import reqparse, Resource, request
from .models import Profile
from ..access import current_user
from ..core import api, access
from ..common import send_access_email, create_access_token, decode_access_token
from ..contant import *
from ..image import avatar2url
from ..users.models import Account

RES = dict(
	username=re.compile(r'^[\w\d]+[\d\w_]+$'),
	password=re.compile(r"""^[\w\d\-\[\]{}|\\,.\/<>;:'"_`~!@#$%^&*()+= ]+$"""),
	email=re.compile(r'^[\w\d]+[\d\w_.]+@([\d\w]+)\.([\d\w]+)(?:\.[\d\w]+)?$'),
)


def get_nickname(uid):
	user = Account.query.get(uid)
	if user is None:
		return u'好酷网友'

	if len(user.username) >= 8:
		return '%s***%s' % (user.username[:3], user.username[-3:])
	return '%s**%s' % (user.username[:3], user.username[-2:])


@access.public
class Profiles(Resource):

	def get(self):
		ids = request.args.getlist('ids', int)
		res = Profile.query.filter(Profile.id.in_(ids))
		profiles = {}
		for profile in res:
			nickname = profile.nickname if profile.nickname else get_nickname(profile.id)
			profiles[profile.id] = {
				'avatar': avatar2url(profile.avatar, size='normal'),
				'nickname': nickname,
			}

		default = current_app.config.get('DEFAULT_AVATAR')
		default_avatar = avatar2url(default, size='normal')
		for id in ids:
			if id not in profiles:
				profiles[id] = {
					'avatar': default_avatar,
					'nickname': u'好酷网友',
				}

		return dict(profiles=profiles)


class ProfileInfo(Resource):

	def __init__(self):
		super(ProfileInfo, self).__init__()
		self.req = reqparse.RequestParser()
		self.req.add_argument('nickname', type=unicode)
		self.req.add_argument('birthday', type=unicode)
		self.req.add_argument('sex', type=unicode)
		self.req.add_argument('city', type=unicode)
		self.req.add_argument('site', type=unicode)
		self.req.add_argument('signature', type=unicode)
		self.req.add_argument('intro', type=unicode)

	def get(self):
		current_user.access_user()
		profile = Profile.query.get(current_user.uid)
		res = dict(profile={})
		if profile is not None:
			res['profile'] = profile.to_dict('id', skip=True)
			default = current_app.config.get('DEFAULT_AVATAR')
			avatar = profile.avatar if profile.avatar else default
			res['profile']['avatar'] = avatar2url(avatar)
		if request.args.get('info') == 'true':
			user = Account.query.get(current_user.uid)
			if user is not None:
				res['info'] = user.to_dict('password', skip=True)
			else:
				res['info'] = {}
		return res

	def post(self):
		current_user.access_user()
		args = strip(self.req.parse_args())
		self.validate(args)
		self.save(args)
		return {}

	def save(self, args):
		save_profile(args)

	def validate(self, args):
		self.validate_sex(args['sex'])
		self.validate_birthday(args['birthday'])

	def validate_birthday(self, birthday):
		pass

	def validate_sex(self, sex):
		if sex not in ['male', 'female']:
			abort(INVALID_ARGS)


class Avatar(Resource):

	def __init__(self):
		super(Avatar, self).__init__()
		self.req = reqparse.RequestParser()
		self.req.add_argument('avatar', type=unicode, required=True)

	def post(self):
		current_user.access_user()
		args = strip(self.req.parse_args())
		save_profile(args)
		return {'avatar':avatar2url(args['avatar'])}


class ChangePassword(Resource):

	def __init__(self):
		super(ChangePassword, self).__init__()
		self.req = reqparse.RequestParser()
		self.req.add_argument('oldpassword', type=unicode, required=True)
		self.req.add_argument('password', type=unicode, required=True)
		self.req.add_argument('repassword', type=unicode, required=True)

	def post(self):
		current_user.access_user()
		args = strip(self.req.parse_args())
		self.validate(args)
		self.update(args)
		return {}

	def update(self, args):
		user = Account.query.get(current_user.uid)
		if not user:
			abort(INVALID_ARGS)

		if user.password == args['oldpassword']:
			if user.password == args['password']:
				abort(NEW_PASSWORD_NEED_DIFF)
			user.password = args['password']
			user.update()
		else:
			abort(PASSWORD_ERROR)

	def validate(self, args):
		self.password_validate(args['password'])
		if args['password'] != args['repassword']:
			abort(REPASSWORD_DIFF) 

	def password_validate(self, password):
		if not password:
			abort(PASSWORD_NULL)

		password_len = len(password)
		if password_len < 6:
			abort(PASSWORD_TOO_SHORT)
		elif password_len > 18:
			abort(PASSWORD_TOO_LONG)
		elif not RES['password'].match(password):
			abort(PASSWORD_FORMAT_ERROR)


class BindEmail(Resource):

	def get(self):
		code = request.args.get('code', '')
		email, t, key = decode_access_token(code)
		user = Account.query.filter_by(email=email).first()
		time_limit = current_app.config.get('EMAIL_TOKEN_TIME_LIMIT')
		if not user or key != user.access_token or time.time() - t > time_limit:
			abort(INVALID_URL)

		user.access_token = 'already_access'
		user.update()
		return {'access':1}

	def post(self):
		current_user.access_user()
		user = Account.query.get(current_user.uid)
		if not user:
			abort(INVALID_ARGS)

		if user.access_token == 'already_access':
			return {'access':1}

		user.access_token, code = create_access_token(user.email, time.time())
		user.update()
		send_access_email(user, code)
		return {'access':0}


def save_profile(args):
	profile = Profile.query.get(current_user.uid)
	if profile is not None:
		for key, val in args.iteritems():
			setattr(profile, key, val)
		profile.update()
	else:
		profile = Profile(id=current_user.uid, **args)
		profile.save()


api.add_resource(Profiles, '/profiles')
api.add_resource(ProfileInfo, '/profile')
api.add_resource(Avatar, '/profile/avatar')
api.add_resource(BindEmail, '/profile/bind_email')
api.add_resource(ChangePassword,  '/profile/change-password')