# coding: utf-8
import os
import datetime
import logging
import conf
from flask import send_from_directory
from werkzeug.routing import BaseConverter
from utils import get_data_path
from ._flask import Flask
from .core import sql, cache, mail, login
from .filters import FilterManager
from .media import MediaManager

filters = FilterManager()
media = MediaManager(
	css=['css/read.min.css'],
	xcss=['libs/bootstrap/css/bootstrap.css', 'dist/css/read.css'],
	js=['js/read.min.js'],
	xjs=['libs/jquery-1.11.1.js','libs/bootstrap/js/bootstrap.js', 'dist/js/read.js'],
)


def apply_route_ext(app):
	class RegexConverter(BaseConverter):
		def __init__(self, url_map, *items):
			super(RegexConverter, self).__init__(url_map)
			self.regex = items[0]

	app.url_map.converters['regex'] = RegexConverter


def init_app(app):
	filters.init_app(app)
	media.init_app(app)
	sql.app = app
	sql.init_app(app)
	cache.init_app(app)
	mail.init_app(app)


def register_routes(app):
	from web import home, topics, articles, about, comments
	app.register_blueprint(home.bp)
	app.register_blueprint(topics.bp, url_prefix='/topics')
	app.register_blueprint(articles.bp, url_prefix='/articles')
	app.register_blueprint(about.bp, url_prefix='/about')
	app.register_blueprint(comments.bp, url_prefix='/comments')

	if app.debug:
		@app.route('/img/<path:filename>')  
		def send_image(filename):
			path = get_data_path(conf.image_file['path'])
			return send_from_directory(path, filename)

	return app


def register_logger(app):
	if app.debug:
		return

	handler = logging.StreamHandler()
	handler.setLevel(logging.ERROR)
	app.logger.addHandler(handler)


def create_app(config=None):
	app = Flask(__name__, template_folder=conf.templates_root + '/read')
	app.config.from_object('web.settings')

	if isinstance(config, dict):
		app.config.update(config)
	elif config:
		app.config.from_pyfile(os.path.abspath(config))

	app.static_folder = app.config.get('STATIC_FOLDER')
	app.config.update({'SITE_TIME': datetime.datetime.utcnow()})

	apply_route_ext(app)
	init_app(app)

	register_routes(app)
	register_logger(app)

	if app.debug and not os.path.exists(app.config['SQLITE_FILE']):
		sql.create_all()

	return app