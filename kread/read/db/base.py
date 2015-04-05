# coding: utf-8
import pymongo

__all__ = [
	'MongoBase',
]


class MongoBase(object):

	def __init__(self, conf):
		self.conn = pymongo.MongoClient(
			conf['host'],
			use_greenlets=conf['use_greenlets'],
		)
		if conf['user']:
			self.conn.admin.authenticate(conf['user'], conf['password'])