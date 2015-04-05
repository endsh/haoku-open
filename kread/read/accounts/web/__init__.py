# coding: utf-8
from simin.web.app import create_app
from accounts.web import users, oauth, profile, settings
from flask import send_from_directory, redirect, url_for
from utils import get_data_path
from .core import init_core


def init_routes(app):
	app.register_blueprint(users.bp, url_prefix='/users')
	app.register_blueprint(oauth.bp, url_prefix='/oauth')
	app.register_blueprint(profile.bp, url_prefix='/profile')

	@app.route('/')
	def index():
		return redirect(url_for('users.login'))

	if app.debug:
		@app.route('/avatar/<path:filename>')  
		def send_image(filename):
			path = get_data_path(app.config.get('AVATAR_FILE_CONF')['path'])
			return send_from_directory(path, filename)

def init_app(app):
	init_core(app)
	init_routes(app)


app = create_app(init_app, settings)
