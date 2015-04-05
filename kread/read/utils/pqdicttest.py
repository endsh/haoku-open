# coding: utf-8
import unittest
from utils.pqdict import PQDict


class PQDictTest(unittest.TestCase):

	def test_pqdict(self):

		def create():
			pq = PQDict(
				values=[
					{'k':1,'v':4},
					{'k':2,'v':3},
					{'k':3,'v':2},
					{'k':4,'v':1},
				],
				key=lambda x: x.value['k'],
				score=lambda x: x.value['v']
			)
			return pq

		pq = create()

		print 'test repr'
		print pq
		print

		print 'test __len__'
		print len(pq)
		print
		
		print 'test __contains__'
		print '1 in pq', 1 in pq
		print '5 in pq', 5 in pq
		print

		print 'test __iter__'
		for i in pq:
			print i
		print

		print 'test __getitem__'
		print pq[1]
		print

		print 'test __setitem__'
		pq[5] = {'k':5, 'v':5}
		for i in pq:
			print i
		try:
			pq[5] = {'v':5}
		except KeyError, e:
			print e
		try:
			pq[7] = {'k':3,'v':7}
		except KeyError, e:
			print e
		print

		print 'test __delitem__'
		del pq[5]
		for i in pq:
			print i
		print

		print 'test pop'
		try:
			while True:
				print pq.pop()
		except KeyError, e:
			print e
		print

		pq = create()
		print 'test popitem'
		try:
			while True:
				print pq.popitem()
		except KeyError, e:
			print e
		print

		pq = create()
		print 'test iterkeys'
		for k in pq.iterkeys():
			print k
		print

		pq = create()
		print 'test itervalues'
		for v in pq.itervalues():
			print v
		print

		pq = create()
		print 'test iteritems'
		for k, v in pq.iteritems():
			print k, v
		print

		pq = create()
		print 'test get'
		print pq.get(1)
		print pq.get(2)
		print pq.get(3)
		print

		pq = create()
		print 'test put'
		pq.put({'k':5, 'v':5})
		for k, v in pq.iteritems():
			print k, v
		print

		with pq.get2do(3) as q:
			q['v'] = 10

		for k, v in pq.iteritems():
			print k, v
		print


if __name__ == '__main__':
	unittest.main()