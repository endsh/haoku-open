# coding: utf-8
from simin.web.app import create_app
from accounts.api.v1 import users, profile, settings
from .core import init_core


def init_routes(app):
	pass


def init_app(app):
	init_core(app)
	init_routes(app)


app = create_app(init_app, settings)
