# coding: utf-8
import json
import time
import requests
from flask import current_app
from .apps import sncode
from .contant import *


class Client(object):

	def __init__(self, user, host):
		self.user = user
		self.host = host
		self.offset = 0
		self.update()

	def update(self, force=False):
		key = 'TIME_OFFSET_OF_%s' % self.__class__.__name__.upper()
		offset = current_app.config.get(key)
		if not force and offset is not None:
			self.offset = offset
			return

		res = self.get('/time')
		if res['code'] == 0:
			self.offset = res['now'] - time.time()
			current_app.config[key] = self.offset
		else:
			current_app.logger.warn('client update err code#%d: %s' 
				% (res['code'], res['msg']))
	
	def time(self):
		return time.time() + self.offset

	def get(self, url, args={}, https=False):
		https = https and not current_app.config.get('DEBUG')
		schema = 'http://' if https else 'http://'
		url = schema + self.host + url
		args.update(self.user.args)
		args['t'] = self.time()
		args['sn'] = sncode(args)

		try:
			if current_app.status != 'RELEASE':
				_args = 'args: %s' % '&'.join('%s=%s' % x for x in args.iteritems())
				current_app.logger.info('API Client (%s) GET: %s\n%s' 
					% (self.__class__.__name__, url, _args))

			rep = requests.get(url, params=args)
			res = rep.json()

			if rep.status_code // 100 == 2:
				res['code'] = 0
			else:
				if 'code' not in res:
					res['code'] = -1
					res['msg'] = u'未知错误'

				if res['code'] == ACCESS_TIMEOUT:
					self.update(force=True)
					rep = requests.get(url, params=args)
					res = rep.json()
					if rep.status_code // 100 == 2:
						res['code'] = 0

			if current_app.status != 'RELEASE':
				current_app.logger.info('resp: %s' % json.dumps(res, indent=4))

			return res
		except ValueError, e:
			current_app.logger.error('error: %s' % str(e))
			current_app.logger.error('error: %s' % rep.content)
			return dict(code=-1, msg=u'未知错误')

	def post(self, url, args={}, data={}, https=False):
		https = https and not current_app.config.get('DEBUG')
		schema = 'http://' if https else 'http://'
		url = schema + self.host + url
		args.update(self.user.args)
		args['t'] = self.time()
		args['sn'] = sncode(args)

		try:
			if current_app.status != 'RELEASE':
				_args = 'args: %s' % '&'.join('%s=%s' % x for x in args.iteritems())
				_data = 'data: %s' % '&'.join('%s=%s' % x for x in data.iteritems())
				current_app.logger.info('API Client (%s) POST: %s\n%s\n%s' 
					% (self.__class__.__name__, url, _args, _data))

			rep = requests.post(url, params=args, data=data)
			res = rep.json()

			if rep.status_code // 100 == 2:
				res['code'] = 0
			else:
				if 'code' not in res:
					res['code'] = -1
					res['msg'] = u'未知错误'
					
				if res['code'] == ACCESS_TIMEOUT:
					self.update(force=True)
					rep = requests.post(url, params=args, data=data)
					res = rep.json()
					if rep.status_code // 100 == 2:
						res['code'] = 0

			if current_app.status != 'RELEASE':
				current_app.logger.info('resp: %s' % json.dumps(res, indent=4))

			return res
		except ValueError, e:
			current_app.logger.error('error: %s' % str(e))
			current_app.logger.error('error: %s' % rep.content)
			return dict(code=-1, msg=u'未知错误')
