# coding:utf-8
import math
import hashlib

__all__ = [
	'MongoComment',
]


class MongoComment(object):

	def __init__(self, db):
		self.db = db
		self.index = db.index
		self.comments = {}
		for a in '0123456789abcdef':
			for b in '0123456789abcdef':
				self.comments[a + b] = db['comments_%s' % (a + b)]

	def comment(self, aid):
		return self.comments[aid[:2]]

	def add(self, aid, row):
		comment = self.comment(aid)			
		art = self.index.find_and_modify({'_id':aid}, {'$inc':{'comments':1}}, True)
		num = art['comments'] / 10 if art is not None else 0
		id = '%s_%d' % (aid, num)
		comment.update(dict(_id=id), {
			'$push':{'comments':row}, 
			'$setOnInsert':{'aid':aid},
		}, True)
		
		return art['comments'] if art is not None else 0

	def count(self, aid):
		res = self.index.find_one(dict(_id=aid)) or {}
		for key in ['comments', 'like', 'unlike']:
			if key not in res:
				res[key] = 0
		return res

	def find(self, aid, page):
		comment = self.comment(aid)
		return comment.find_one({'_id':'%s_%d' % (aid, page)})