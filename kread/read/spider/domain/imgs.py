# coding: utf-8
from collections import OrderedDict, defaultdict


class Images(object):

	def __init__(self, domain):
		self.domain = domain
		self.domains = domain.domains
		self.log = domain.log
		self.handle = domain.domains.master.articles.img_arts
		self.queue = OrderedDict()
		self.waiting = defaultdict(list)

	def __contains__(self, key):
		return key in self.queue

	def __nonzero__(self):
		return len(self.queue) > 0

	def __len__(self):
		return len(self.queue)

	def waits(self):
		count = 0
		for imgs in self.waiting.itervalues():
			count += len(imgs)
		return count

	def put(self, img):
		if img['_id'] not in self.queue \
				and not self.domains.is_fetching(img['_id']):
			self.queue[img['_id']] = img
			return True

		self.waiting[img['_id']].append(img)
		return True

	def get(self):
		if self.queue:
			return self.queue.popitem()[1]

	def cancel(self, img):
		self.queue[img['_id']] = img

	def fetch(self, img, res):
		self.handle.fetch(img, res)
		imgs = self.waiting.pop(img['_id'], None)
		if imgs is not None:
			for img in imgs:
				self.handle.fetch(img, res)