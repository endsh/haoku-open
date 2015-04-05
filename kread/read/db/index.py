# coding: utf-8
import pymongo
import math
import hashlib
from utils import unicode2hash, str2hash

__all__ = [
	'MongoIndex',
]


class MongoIndex(object):

	def __init__(self, db):
		self.db = db
		self.indexs = {}
		for a in '0123456789abcdef':
			for b in '0123456789abcdef':
				self.indexs[a + b] = db['index_%s' % (a + b)]

	def rank(self, each):
		return (min(each['n'], 8) + math.log(each['p'] + 1)) * 100 + (each['t'] - 946656000.0) / 900

	def add(self, word, id, num, pic, pubtime, icons):
		word = word.lower()
		index = self.index(word)
		res = index.find_and_modify(
			query={'_id':word}, 
			update={'$pull':{'index':{'i':id}}},
			fields={'icon':1, 'icon_time':1},
		)

		each = {'i':id, 'n':num, 'p':pic, 't':pubtime}
		each['r'] = self.rank(each)
		doc = {'$push': {'index':{'$each':[each], '$slice':1000, '$sort':{'r':-1}}}}
		if icons and (res is None or not res['icon'] or pubtime - res['icon_time'] > 86400):
			icon = icons.pop()['path']
			doc['$set'] = {'icon':icon, 'icon_time':pubtime}
		else:
			doc['$setOnInsert'] = {'icon':'', 'icon_time':0}
		index.update({'_id':word}, doc, True)

	def remove(self, word, id):
		word = word.lower()
		index = self.index(word)
		index.update({'_id':word}, {'$pull':{'index':{'i':id}}})

	def index(self, word):
		md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
		return self.indexs[md]

	def find(self, word, fields=None):
		word = word.lower()
		index = self.index(word)
		return index.find_one({'_id':word}, fields=fields)

	def drop(self):
		for index in self.indexs.itervalues():
			index.drop()


class MongoReIndex(object):

	def __init__(self, db):
		self.db = db
		self.index = db.index
		self.keys = db.index_keys
		# self.indexs = {}
		# for a in range(100):
		# 	self.indexs[a] = db['index_%d' % a]

	def rank(self, num, imgs, pubtime):
		return int((min(num, 10) + math.log(imgs + 1)) * 30 + (pubtime - 946656000.0) / 3600)

	def add(self, word, id, num, imgs, pubtime, icons):
		word = word.lower()
		whash = unicode2hash(word)
		res = self.index.find_one({'_id':word})

		row = {
			'_id': str2hash('%d-%s' % (whash, id)),
			'article': id,
			'word': whash,
			'num': num,
			'imgs': imgs,
			'pubtime': pubtime,
			'rank': self.rank(num, imgs, pubtime)
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

		if res['count'] >= 2:
			if res['count'] >= 1500:
				words = list(self.keys.find({'word':whash}).sort([('rank', -1)]).skip(999).limit(1))
				if words:
					self.keys.remove({'word':whash, 'rank':{'$lt':words[0]['rank']}})
					res['rank'] = words[0]['rank']

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

	def remove(self, doc):
		return self.keys.remove(doc)

	def get_index(self, md):
		# return self.indexs[md]
		return self.keys

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