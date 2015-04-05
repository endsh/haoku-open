# coding: utf-8
from collections import OrderedDict


class Pages(object):

	def __init__(self, domain):
		self.domain = domain
		self.domains = domain.domains
		self.handle = domain.domains.master.articles.pag_arts
		self.queue = OrderedDict()

	def __nonzero__(self):
		return len(self.queue) > 0

	def __len__(self):
		return len(self.queue)

	def put(self, page):
		if page['_id'] not in self.queue \
				and not self.domains.is_fetching(page['_id']):
			self.queue[page['_id']] = page
			return True
		return False

	def get(self):
		if self.queue:
			return self.queue.popitem()[1]

	def cancel(self, page):
		self.queue[page['_id']] = page

	def fetch(self, page, res):
		self.handle.fetch(page, res)
