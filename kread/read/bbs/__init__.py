# coding: utf-8
from simin.web.app import create_app
from bbs import home, settings
from .core import init_core


def init_routes(app):
	app.register_blueprint(home.bp, url_prefix='/home')


def init_app(app):
	init_core(app)
	init_routes(app)


app = create_app(init_app, settings)