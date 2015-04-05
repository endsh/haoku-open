# coding: utf-8
import time


class Templates(object):

	def __init__(self, domain):
		self.domain = domain
		self.mongo = domain.domains.template
		self.log = domain.log
		self.tpls = dict()

	def __contains__(self, tpl):
		return tpl in self.tpls

	def __len__(self):
		return len(self.tpls)

	def put(self, tpl):
		if tpl['_id'] not in self.tpls:
			self.tpls[tpl['_id']] = tpl
		else:
			keys = ['title_selecotr', 'source_selector', 'content_selector']
			for key in keys:
				self.tpls[tpl['_id']][key] = key
			self.tpls[tpl['_id']]['last'] = time.time()

	def load(self):
		doc = {
			'domain': self.domain.id(),
			'status': 'common',
		}
		tpls = self.mongo.find(doc)
		for tpl in tpls:
			if tpl not in self.tpls:
				self.tpls[tpl['_id']] = tpl
		self.log.info('load %s tpls from %s.'
			% (tpls.count(), self.domain.id()))

	def back(self, start, end):
		tpls = {}
		for tpl in self.tpls.itervalues():
			if start < tpl['last'] <= end:
				tpls[tpl['_id']] = tpl
		return tpls

	def selector(self, tpl):
		if tpl in self.tpls:
			tpl = self.tpls[tpl]
			return {
				'title_selector': tpl['title_selector'],
				'source_selector': tpl['source_selector'],
				'content_selector': tpl['content_selector'],
			}
		return {}