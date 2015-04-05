# coding: utf-8
import conf
from flask import send_from_directory
from simin.web.app import create_app
from web import home, topics, articles, about#, comments
from web import settings
from utils import get_data_path
from .core import init_core


def init_routes(app):
	app.register_blueprint(home.bp)
	app.register_blueprint(topics.bp, url_prefix='/topics')
	app.register_blueprint(articles.sp, url_prefix='/articles')
	app.register_blueprint(articles.bp, url_prefix='/a')
	app.register_blueprint(about.bp, url_prefix='/about')
	# app.register_blueprint(comments.bp, url_prefix='/comments')

	if app.debug:
		@app.route('/img/<path:filename>')  
		def send_image(filename):
			path = get_data_path(conf.image_file['path'])
			return send_from_directory(path, filename)


def init_app(app):
	init_core(app)
	init_routes(app)


app = create_app(init_app, settings)