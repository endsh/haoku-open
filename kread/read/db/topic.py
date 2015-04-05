# coding: utf-8
import pymongo
import math
import hashlib
from utils import unicode2hash, str2hash

__all__ = [
	'MongoTopic', 'MongoReTopic'
]


class MongoTopic(object):

	def __init__(self, db):
		self.db = db
		self._index = db['index']

	def rank(self, each):
		return math.log(each['p'] + 1) * 5 + (each['t'] - 946656000.0) / 3600

	def add(self, word, id, pic, pubtime):
		word = word.lower()
		index = self.index(word)
		res = index.update({'_id':word}, {'$pull':{'index':{'i':id}}})

		each = {'i':id, 'p':pic, 't':pubtime}
		each['r'] = self.rank(each)
		doc = {'$push': {'index':{'$each':[each], '$slice':1000, '$sort':{'r':-1}}}}
		index.update({'_id':word}, doc, True)

	def remove(self, word, id):
		word = word.lower()
		index = self.index(word)
		index.update({'_id':word}, {'$pull':{'index':{'i':id}}})

	def index(self, word):
		return self._index

	def find(self, word, fields=None):
		word = word.lower()
		index = self.index(word)
		return index.find_one({'_id':word}, fields=fields)

	def drop(self):
		self._index.drop()


class MongoReTopic(object):

	def __init__(self, db):
		self.db = db
		self.index = db.topic
		self.keys = db.topic_keys
		# self.indexs = {}
		# for a in range(100):
		# 	self.indexs[a] = db['index_%d' % a]

	def rank(self, imgs, pubtime):
		return int(math.log(imgs + 1) * 5 + (pubtime - 946656000.0) / 3600)

	def add(self, word, id, imgs, pubtime, icons):
		word = word.lower()
		whash = unicode2hash(word)
		res = self.index.find_one({'_id':word})

		row = {
			'_id': str2hash('%d-%s' % (whash, id)),
			'article': id,
			'word': whash,
			'imgs': imgs,
			'pubtime': pubtime,
			'rank': self.rank(imgs, pubtime)
		}

		if res is None:
			res = {
				'_id': word,
				'word': whash,
				'rank': 0,
				'count': 0,
				'icon': '',
				'icon_time': 0,
				'auto': True,
			}

		if res['count'] >= 1500:
			words = list(self.keys.find({'word':whash}).sort([('rank', -1)]).skip(999).limit(1))
			if words:
				self.keys.remove({'word':whash, 'rank':{'$lt':words[0]['rank']}})
				res['rank'] = words[0]['rank']
			res['count'] = 1000

		if row['rank'] > res['rank']:
			if icons and res['auto'] == True and pubtime - res['icon_time'] > 3 * 86400:
				res['icon'] = icons.pop()
				res['icon_time'] = pubtime
			self.keys.save(row)
			res['count'] += 1
			self.index.save(res)

	def find(self, word, last=None, limit=20, fields=None):
		word = word.lower()
		whash = unicode2hash(word)
		count = self.keys.find({'word':whash}).count()
		if last is None:
			return count, list(self.keys.find({'word':whash}, fields=fields).sort([('pubtime',pymongo.DESCENDING)]).limit(limit))

		last = self.keys.find_one({'word':whash, 'article':last}, {'pubtime':1})
		if last is None:
			return count, []
		pubtime = last['pubtime']
		topic = self.keys.find({'word':whash, 'pubtime':{'$lt':pubtime}}, fields=fields).sort([('pubtime',pymongo.DESCENDING)])
		return count, list(topic.limit(limit))

	def find_page(self, word, page, limit=20, fields=None):
		skip = page * limit - limit
		word = word.lower()
		whash = unicode2hash(word)
		topic = self.keys.find({'word':whash}, fields=fields).sort([('pubtime',pymongo.DESCENDING)])
		return topic.count(), list(topic.skip(skip).limit(limit))

	def find_index(self, word, fields=None):
		word = word.lower()
		return self.index.find_one({'_id':word}, fields=fields)

	def find_tags(self, tags, fields=None):
		return self.index.find({'_id':{'$in':tags}}, fields=fields)

	def get_index(self, md):
		# return self.indexs[md]
		return self.keys

	def remove(self, doc):
		return self.keys.remove(doc)

	def create_index(self):
		self.index.create_index([('word', pymongo.ASCENDING)])
		self.index.create_index([('count', pymongo.ASCENDING)])
		# for index in self.indexs.itervalues():
		# 	index.create_index([('word', pymongo.ASCENDING)])
		# 	index.create_index([('word', pymongo.ASCENDING), ('rank', pymongo.DESCENDING)])
		# 	index.create_index([('word', pymongo.ASCENDING), ('pubtime', pymongo.DESCENDING)])
		self.keys.create_index([('word', pymongo.ASCENDING)])
		self.keys.create_index([('word', pymongo.ASCENDING), ('rank', pymongo.DESCENDING)])
		self.keys.create_index([('word', pymongo.ASCENDING), ('pubtime', pymongo.DESCENDING)])
		self.keys.create_index([('article', pymongo.ASCENDING)])

	def drop(self):
		self.index.drop()
		# for index in self.indexs.itervalues():
		# 	index.drop()
		self.keys.drop()