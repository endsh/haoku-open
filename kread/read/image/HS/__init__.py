#coding: utf-8
import os
import datetime
import logging
import hashlib
from flask import request, g
from flask.ext.login import LoginManager
from werkzeug.routing import BaseConverter

import conf
from HS._flask import Flask
from HS.core import db, mongo, cache


def create_app(config=None):
	app = Flask(
		__name__, 
		template_folder='templates',
	)

	app.config.from_pyfile('_settings.py')

	if isinstance(config, dict):
		app.config.update(config)
	elif config:
		app.config.from_pyfile(os.path.abspath(config))

	app.static_folder = app.config.get('STATIC_FOLDER')
	app.config.update({'SITE_TIME' : datetime.datetime.utcnow()})

	apply_route_ext(app)

	register_jinjia(app)
	register_database(app)

	register_login(app)
	register_routes(app)
	register_logger(app)

	if app.debug and not os.path.exists(app.config['SQLITE_FILE']):
		db.create_all()

	return app


def apply_route_ext(app):
	class RegexConverter(BaseConverter):
		def __init__(self, url_map, *items):
			super(RegexConverter, self).__init__(url_map)
			self.regex = items[0]


def register_jinjia(app):
	from HS import filters

	if not hasattr(app, '_static_hash'):
		app._static_hash = {}

	def static_url(filename):
		if filename in app._static_hash:
			return app._static_hash[filename]

		path = os.path.join(app.static_folder, filename)
		if not os.path.isfile(path):
			return filename

		with open(path, 'r') as f:
			content = f.read()
			hsh = hashlib.md5(content).hexdigest()

		prefix = app.config.get('SITE_STATIC_PREFIX', '/static/')
		value = '%s%s?v=%s' % (prefix, filename, hsh[:5])
		app._static_hash[filename] = value
		return value

	def static_meta():
		if app.debug:
			out = []
			css = ['libs/bootstrap/css/bootstrap.css', 'dist/css/dash.css']
			out.extend(map(lambda x: '<link rel="stylesheet" href="/static/%s">' % x, css))

			js = ['libs/jquery-1.11.1.js', 'libs/bootstrap/js/bootstrap.js', 'dist/js/dash.js']
			out.extend(map(lambda x: '<script src="/static/%s"></script>' % x, js))
			return filters.auto_markup('\n'.join(out))

		return filters.auto_markup('<link rel="stylesheet" href="%s">\n<script src="%s"></script>' % (
			static_url('css/dash.min.css'), static_url('js/dash.min.js')))


	@app.context_processor
	def register_context():
		return dict(
			static_url=static_url,
			static_meta=static_meta,
			enumerate=enumerate,
		)

	filters.init_app(app)

def register_database(app):
	db.init_app(app)
	db.app = app
	mongo.init_app(app)
	cache.init_app(app)

def register_login(app):
	login_manager = LoginManager()
	login_manager.login_view = 'account.login'
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(app):
		return Acount.query.get(user_id)

def register_routes(app):
	from HS import getter
	app.register_blueprint(getter.bp, url_prefix='/getter')
	return app

def register_logger(app):
	if app.debug:
		return

	handler = logging.StreamHandler()
	handler.setLevel(logging.ERROR)
	app.logger.addHandler(handler)