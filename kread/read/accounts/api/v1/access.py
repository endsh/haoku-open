# coding: utf-8
import base64
import binascii
import time
from flask import request, jsonify, current_app
from werkzeug.security import safe_str_cmp
from accounts.sdk.access import AccessManager as _AccessManager
from accounts.sdk.access import current_user, access_service
from .contant import *
from .token import create_token
from .users import Account
from .image import avatar2url


class AccessManager(_AccessManager):

	def __init__(self, app=None, access_url='/access', time_url='/time'):
		super(AccessManager, self).__init__(app, access_url)
		self._public = ['server_time']

	def init_app(self, app):
		app.access = self

		@app.route(self.access_url)
		@access_service
		def access():
			return self.access()

		@app.route(self.time_url)
		def server_time():
			return jsonify({'now':time.time()})

		@app.before_request
		def before_request():
			if request.endpoint in self._public:
				self.public_access()
			else:
				current_user.access()

		from .profile import Profile

	def access(self):
		from .profile.models import Profile
		appid = request.args.get('appid', 0, int)
		token = request.args.get('token')

		if not token or not appid:
			abort(ACCESS_DENIED)

		try:
			decode = base64.b64decode(token)
		except binascii.Error:
			abort(ACCESS_DENIED)

		infos = decode.split('|')
		if len(infos) != 3:
			abort(ACCESS_DENIED)

		try:
			uid, t, _ = infos
			uid, t = int(uid), float(t)
		except ValueError:
			abort(ACCESS_DENIED)

		user = Account.query.get(uid)
		if user is None:
			abort(ACCESS_DENIED)

		build = create_token(appid, uid, user.password.hash, t)
		if not safe_str_cmp(token, build):
			abort(ACCESS_DENIED)

		if time.time() - t > current_app.config.get('TOKEN_TIMEOUT_LIMIT', 86400 * 180):
			abort(INVALID_TOKEN)

		default = current_app.config.get('DEFAULT_AVATAR')
		profile = Profile.query.get(uid)
		avatar = profile.avatar if profile and profile.avatar else default
		return jsonify(dict(
			user={
				'uid': uid,
				'username': user.username,
				'avatar': avatar2url(avatar),
			},
		))
