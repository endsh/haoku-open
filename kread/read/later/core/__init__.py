# coding: utf-8
from flask import jsonify
from conf import mongo_web
from db import MongoLater

mongo = MongoLater(mongo_web)


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