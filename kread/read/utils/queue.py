# coding: utf-8
import time
from gevent import queue


class KeyItem(dict):
	""" dict cmp with key """

	def __init__(self, item, priority=0, reverse=False): 
		""" init class with item """
		super(KeyItem, self).__init__(item)
		self.priority = priority
		self.reverse = reverse

	def __cmp__(self, other):
		""" cmp with item key """
		return cmp(self.priority, other.priority) * (-1 if self.reverse else 1)


class KeyQueue(queue.PriorityQueue):
	""" priority queue cmp with queue """

	def __init__(self, maxsize=None, items=None, reverse=False):
		""" init class """
		super(KeyQueue, self).__init__(maxsize=maxsize)
		self.reverse = reverse
		if items:
			for item in items:
				self.put(item)

	def get(self):
		""" get item """
		return dict(super(KeyQueue, self).get())

	def put(self, item, priority=0):
		""" put item """
		super(KeyQueue, self).put(KeyItem(item, priority, self.reverse))

	def to_list(self):
		""" to list """
		res, items = [], self.copy()
		while not items.empty():
			res.append(items.get())
		return res

	def to_dict(self, key):
		res = self.to_list()
		return dict((x[key], x) for x in res)


class TimeQueue(KeyQueue):
	""" priority queue base time """

	def __init__(self, maxsize=None, items=None, reverse=False, maxpri=0):
		""" init class """
		self.maxpri = maxpri
		super(TimeQueue, self).__init__(maxsize, items, reverse)

	def put(self, item, priority=0):
		""" put item """
		priority = min(self.maxpri, priority) if self.maxpri else priority
		super(TimeQueue, self).put(item, time.time() + priority)
