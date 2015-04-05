# coding: utf-8
import os
import logging
from werkzeug.routing import BaseConverter
from flask import Blueprint
from ._flask import Flask
from .filters import FilterManager

filters = FilterManager()
root_folder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
template_folder = os.path.join(root_folder, 'templates')
blueprint = Blueprint('simin', 'simin', template_folder=template_folder)


class RegexConverter(BaseConverter):

	def __init__(self, url_map, *items):
		super(RegexConverter, self).__init__(url_map)
		self.regex = items[0]


def init_coverter(app):
	app.url_map.converters['regex'] = RegexConverter


def init_filters(app):
	filters.init_app(app)


def init_logger(app):
	if app.debug:
		return

	handler = logging.StreamHandler()
	handler.setLevel(logging.ERROR)
	app.logger.addHandler(handler)


def create_app(init_app, settings):
	app = Flask(__name__, template_folder=settings.TEMPLATE_FOLDER)
	app.config.from_object(settings)
	app.static_folder = app.config.get('STATIC_FOLDER')
	app.status = app.config.get('STATUS')
	app.register_blueprint(blueprint)
	init_coverter(app)
	init_filters(app)
	init_logger(app)
	init_app(app)
	return app