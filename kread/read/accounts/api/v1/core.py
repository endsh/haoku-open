# coding: utf-8
from simin.web.core import api, cache, sql, mail
from simin.web.core import api_success, create_db
from .access import AccessManager

access = AccessManager()


def init_core(app):
	api.init_app(app)
	cache.init_app(app)
	sql.init_app(app)
	sql.app = app
	mail.init_app(app)
	create_db(app)

	access.init_app(app)