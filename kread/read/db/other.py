# coding: utf-8
import pymongo


class MongoLater(object):
	""" spider mongodb connection class """

	def __init__(self, conf):
		self.conn = pymongo.MongoClient(
			conf['host'],
			use_greenlets=conf['use_greenlets'],
		)
		if conf['user']:
			self.conn.admin.authenticate(conf['user'], conf['password'])
		self.db = self.conn.later
		self.article = self.db['article']

	def clear(self):
		self.clear_db()

	def clear_db(self):
		self.conn.drop_database('later')


class MongoGetter(object):
	""" spider mongodb connection class """

	def __init__(self, conf):
		self.conn = pymongo.MongoClient(
			conf['host'],
			use_greenlets=conf['use_greenlets'],
		)
		if conf['user']:
			self.conn.admin.authenticate(conf['user'], conf['password'])
		self.db = self.conn.getter
		self.domain = self.db['domain']
		self.catecory = self.db['catecory']
		self.template = self.db['template']
		self.link = self.db['link']
		self.word = self.db['word']

	def clear(self):
		self.clear_db()

	def clear_db(self):
		self.conn.drop_database('getter')


class MongoBest(object):
	""" spider mongodb connection class """

	def __init__(self, conf):
		self.conn = pymongo.MongoClient(
			conf['host'],
			use_greenlets=conf['use_greenlets'],
		)
		if conf['user']:
			self.conn.admin.authenticate(conf['user'], conf['password'])
		self.db = self.conn.best
		self.domain = self.db['domain']
		self.catecory = self.db['catecory']
		self.template = self.db['template']

	def clear(self):
		self.clear_db()

	def clear_db(self):
		self.conn.drop_database('best')
