# coding: utf-8
from simin.web.app import create_app
from api.v1 import articles, topics, settings
from .core import init_core


def init_app(app):
	init_core(app)


app = create_app(init_app, settings)