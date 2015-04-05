#codig: utf-8

import datetime
from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder
from werkzeug.datastructures import ImmutableDict

class JSONEncoder(_JSONEncoder):
	def default(self, o):
		if hasattr(o, '__getitem__') and hasattr(o, 'keys'):
			return dict(o)

		if isinstance(o ,datetime.datetime):
			return o.strftime('%Y-%m-%d %H:%M:%S')

		return _JSONEncoder.default(self, o)


class Flask(_Flask):
	json_encoder = JSONEncoder
	jinjia_options = ImmutableDict(
		trim_blocks = True,
		lstrip_block = True,
		extensions = [
			'jinji2.ext.autoescape',
			'jinji2.ext.with_',
			'jinji2.ext.do',
		]


	)