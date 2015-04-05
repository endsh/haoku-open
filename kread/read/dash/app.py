# coding: utf-8
import os
import datetime
import logging
import conf
from flask import request
from flask.ext.login import current_user
from werkzeug.routing import BaseConverter
from ._flask import Flask
from .core import admin, db, cache, mail, login
from .account.models import Account
from .filters import FilterManager
from .media import MediaManager
from .mongo import register_mongo_admin

filters = FilterManager()
media = MediaManager(
	css=['css/dash.min.css'],
	xcss=[
		'libs/bootstrap/css/bootstrap.css', 
		'libs/bootstrap/css/bootstrap-datetimepicker.css',
		'libs/flask-admin/css/select2.css',
		'libs/font-awesome-4.1.0/css/font-awesome.css',
		'libs/metisMenu/metisMenu.css',
		'libs/morris/morris.css',
		'libs/sb-admin-2/sb-admin-2.css',
		'libs/plugins/timeline.css',
		'dist/css/dash.css',
	],
	js=['js/dash.min.js'],
	xjs=[
		'libs/jquery-1.11.1.js', 
		'libs/jquery.form.js',
		'libs/bootstrap/js/bootstrap.js',
		'libs/flask-admin/js/select2.min.js',
		'libs/table-fixed-header.js',
		'dist/js/dash.js',
	],
	jsfooter=['js/dash-footer.min.js'],
	xjsfooter=[
		'libs/metisMenu/metisMenu.js',
		'libs/sb-admin-2/sb-admin-2.js',
		'libs/flot/jquery.flot.js',
		'src/js/control.js'
	],
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
	admin.init_app(app)
	db.app = app
	db.init_app(app)
	cache.init_app(app)
	mail.init_app(app)

	login.init_app(app)
	login.login_view = 'account.login'

	@login.user_loader
	def load_user(user_id):
		return Account.query.get(user_id)

	@app.before_request
	def before_request():
		if not current_user.is_authenticated() \
				and request.endpoint not in [login.login_view, 'static']:
			return app.login_manager.unauthorized()


def register_admin(app):
	register_mongo_admin(app)


def register_routes(app):
	from dash import home, account, mongo, control, log, distance
	app.register_blueprint(home.bp, url_prefix='')
	app.register_blueprint(log.bp, url_prefix='/log')
	app.register_blueprint(account.bp, url_prefix='/account')
	app.register_blueprint(control.bp, url_prefix='/control')
	app.register_blueprint(distance.bp, url_prefix='/distance')
	# app.register_blueprint(test.bp, url_prefix='/test')
	return app


def register_logger(app):
	if app.debug:
		return

	handler = logging.StreamHandler()
	handler.setLevel(logging.ERROR)
	app.logger.addHandler(handler)


def create_app(config=None):
	app = Flask(__name__, template_folder=conf.templates_root + '/dash')
	app.config.from_object('dash.settings')
	if isinstance(config, dict):
		app.config.update(config)
	elif config:
		app.config.from_pyfile(os.path.abspath(config))

	app.static_folder = app.config.get('STATIC_FOLDER')
	app.config.update({'SITE_TIME': datetime.datetime.utcnow()})

	apply_route_ext(app)
	init_app(app)

	register_admin(app)
	register_routes(app)
	register_logger(app)

	dbfile = os.path.join(app.config['ROOT_FOLDER'], app.config['SQLITE_FILE'])
	if app.debug and not os.path.exists(dbfile):
		db.create_all()
		Account(
			username=u'流光',
			password='jiaqing520',
			email='438985635@qq.com',
			email_verify='already_verify',
			phone='13417171519',
			phone_verify='already_verify',
		).save()
		Account(
			username=u'xiaoshuai',
			password='123456',
			email='123456@qq.com',
			email_verify='already_verify',
			phone='123456',
			phone_verify='already_verify',
		).save()
	return app