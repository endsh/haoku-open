# coding: utf-8
import os
import random
import string
from cStringIO import StringIO
from flask import current_app, session, request, make_response
from wheezy.captcha import image

__all__ = [
	'VerifyManager', 'get_verify_code', 'on_validate_code',
]

_keys = set()
_codes = string.uppercase + string.digits

FONT_PATH = os.path.dirname(__file__)
FONTS = [os.path.join(FONT_PATH, 'fonts/ERASDEMI.TTF')]
BG_COLORS = ['#ffffff', '#fbfbfb', '#fdfeff']
TEXT_COLORS = ['#39f', '#3f9', '#93f', '#9f3', '#f93', '#f39']


class VerifyManager(object):

	def __init__(self, app=None, code_url='/verify_code'):
		self.code_url = code_url
		if app is not None:
			self.init_app(app)

	def init_app(self, app):
		app.verify = self

		@app.route(self.code_url)
		def verify_code():
			key = request.args.get('key', None)
			if key not in _keys:
				return ''
			code, _ = get_verify_code(key, refresh=True)
			return code2image(code)


def get_verify_code(key, refresh=False):
	_keys.add(key)

	if 'verify_codes' not in session:
		session['verify_codes'] = {}

	code_len = current_app.config.get('VERIFY_CODE_LEN', 4)
	codes = session['verify_codes']
	if key not in codes or refresh:
		codes[key] = {
			'code': ''.join(random.sample(_codes, code_len)),
			'times': 0,
		}

	return codes[key]['code'], codes[key]['times']


def on_validate_code(key):
	if 'verify_codes' not in session:
		session['verify_codes'] = {}

	codes = session['verify_codes']
	if key in codes:
		codes[key]['times'] += 1


def code2image(code):
	size = current_app.config.get('VERIFY_CODE_FONT_SIZE', 40)
	drawer = image.captcha(
		drawings=[
			image.background(random.choice(BG_COLORS)),
			image.text(
				fonts=FONTS, 
				font_sizes=(size, size + 2, size + 2),
				color=random.choice(TEXT_COLORS), 
				drawings=[image.rotate(), image.offset()],
			),
		],
		width=size * len(code),
		height=size + 4,
	)
	buf = StringIO()
	pic = drawer(code)
	pic.save(buf, 'GIF')
	response = make_response(buf.getvalue())
	response.headers['Content-Type'] = 'image/gif'
	return response