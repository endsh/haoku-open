# coding: utf-8
import conf
import xmlrpclib
from flask import jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.cache import Cache
from flask.ext.mail import Mail
from flask.ext.login import LoginManager

import conf
from db import MongoIWeb, MongoAdmin


admin = Admin(template_mode='bootstrap3')
db = SQLAlchemy()
cache = Cache()
mail = Mail()
login = LoginManager()
counter = xmlrpclib.ServerProxy("http://%s:%d" % conf.count_conf['listener'])

mongo_iweb = MongoIWeb(conf.mongo_iweb)
mongo_admin = MongoAdmin(conf.mongo_iweb)

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


def json_success(**kwargs):
	kwargs['code'] = 0
	return jsonify(kwargs)


def json_error(**kwargs):
	kwargs['code'] = 1
	return jsonify(kwargs)