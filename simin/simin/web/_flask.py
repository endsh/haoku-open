# coding: utf-8
import datetime
from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder
from werkzeug.datastructures import ImmutableDict

__all__ = [
	'JSONEncoder', 'Flask',
]


class JSONEncoder(_JSONEncoder):

	def default(self, obj):
		if hasattr(obj, '__getitem__') and hasattr(obj, 'keys'):
			return dict(obj)
		if isinstance(obj, datetime.datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')
		return _JSONEncoder.default(self, obj)


class Flask(_Flask):

	json_encoder = JSONEncoder
	jinja_options = ImmutableDict(
		trim_blocks=True,
		lstrip_blocks=True,
		extensions=[
			'jinja2.ext.autoescape',
			'jinja2.ext.with_',
			'jinja2.ext.do',
		],
	)