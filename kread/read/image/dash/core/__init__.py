# coding: utf-8
from flask import jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mongoengine import MongoEngine
from flask.ext.cache import Cache

import conf

# database and cache
db = SQLAlchemy()
mongo = MongoEngine()
cache = Cache()


class SessionMixin(object):
	def to_dict(self, *columns):
		dct = {}
		for col in columns:
			value = getattr(self, col)
			if isinstance(value, datetime.datetime):
				value = value.strftime('%Y-%m-%d %H:%M:%S')
			dct[col] = value
		return dct

	def save(self):
		db.session.add(self)
		db.session.commit()
		return self

	def delete(self):
		db.session.delete(self)
		db.session.commit()
		return self


def json_success(*args, **kwargs):
	kwargs['code'] = 0
	return jsonify(kwargs)


def json_error(*args, **kwargs):
	kwargs['code'] = 1
	return jsonify(kwargs)