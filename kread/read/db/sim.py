# coding: utf-8
import sys
import pymongo

__all__ = [
	'MongoSim',
]


class MongoSim(object):

	def __init__(self, db):
		self.db = db
		self.sim = db['sim']
		self.sims = [db['sim%d' % i] for i in xrange(4)]

	def num2parts(self, num):
		num = num + sys.maxint
		return [int((num & (65535 << i)) >> i) for i in (0, 16, 32, 48)]

	def near(self, num):
		nums = set()
		parts = self.num2parts(num)
		for i, sim in enumerate(self.sims):
			for row in sim.find({'part':parts[i]}, {'_id':1}):
				nums.add(row['_id'])
		for n in nums:
			if self.distance(num, n) <= 3:
				return n

	def unset(self, _id, key):
		if key == True:
			row = self.sim.find_one({'_id':_id})
			if row:
				for sim in self.sims:
					sim.remove({'_id':row['num']})
				if row['ids']:
					row['_id'], row['num'] = row['ids'].popitem()
					parts = self.num2parts(row['num'])
					for i, sim in enumerate(self.sims):
						sim.save({'_id':row['num'], 'part':parts[i]})
					self.sim.save(row)
		elif key != False:
			self.sim.update({'_id':key}, {'$unset':{'ids.%s' % _id:''}})

	def save(self, _id, num, near):
		if near is not None:
			row = self.sim.find_one({'num':near}, {'_id':1})
			if row:
				if row['_id'] == _id:
					return True
				self.sim.update({'_id':row['_id']}, {'$set':{'ids.%s' % _id:num}})
				return row['_id']
		
		parts = self.num2parts(num)
		for i, sim in enumerate(self.sims):
			sim.save({'_id':num, 'part':parts[i]})
		self.sim.save({
			'_id':_id,
			'num':num,
			'ids':{},
		})
		return True

	def distance(self, num, other):
		num = num + sys.maxint
		other = other + sys.maxint
		x = (num ^ other) & ((1 << 64) - 1)
		ans = 0
		while x:
			ans += 1
			x &= x - 1
		return ans

	def create_index(self):
		self.sim.create_index([('num', pymongo.ASCENDING)])
		for sim in self.sims:
			sim.create_index([('part', pymongo.ASCENDING)])

	def drop(self):
		self.sim.drop()
		for sim in self.sims:
			sim.drop()