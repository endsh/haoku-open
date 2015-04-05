# coding: utf-8
import os
import datetime
from flask import jsonify
from flask.ext.admin import Admin
from flask.ext.cache import Cache
from flask.ext.sendmail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from .api import Api


admin = Admin(template_mode='bootstrap3')
api = Api(catch_all_404s=True)
cache = Cache()
sql = SQLAlchemy()
mail = Mail()


class SessionMixin(object):

	def to_dict(self, *columns, **kwargs):
		dct = {}
		if not columns:
			columns = self.columns

		if kwargs.pop('skip', None) == True:
			columns = [x for x in self.columns if x not in columns]

		for col in columns:
			value = getattr(self, col)
			if isinstance(value, datetime.datetime):
				value = value.strftime('%Y-%m-%d %H:%M:%S')
			dct[col] = value
		return dct

	@property
	def columns(self):
		return [x.name for x in self.__table__.columns]

	def save(self):
		sql.session.add(self)
		sql.session.commit()
		return self

	def update(self, **kwargs):
		for key,value in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, value)
			else:
				raise KeyError("Object '%s' has no field '%s'." % (type(object), key))
		sql.session.commit()
		return self

	def delete(self):
		sql.session.delete(self)
		sql.session.commit()
		return self


def create_db(app, release=False):
	if release == True:
		sql.create_all()
	elif app.status == 'RELEASE':
		return

	if not os.path.exists(app.config.get('SQLITE_FILE')):
		sql.create_all()


def api_success(**kwargs):
	kwargs['code'] = 0
	return kwargs


def json_success(**kwargs):
	kwargs['code'] = 0
	return jsonify(kwargs)


def json_error(code=-1, **kwargs):
	kwargs['code'] = code
	return jsonify(kwargs)
