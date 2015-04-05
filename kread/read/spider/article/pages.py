# coding: utf-8
import time
from .base import ArtBase


class Art2Page(ArtBase):

	def __init__(self, articles):
		super(Art2Page, self).__init__(
			articles=articles,
			cmd='pag',
		)
		self.domains = self.master.domains

	def is_done(self, article):
		if not article['pages']:
			return True

		for page in article['pages'].itervalues():
			if page['status'] != 'done':
				return False
		return True

	def update_ext(self, page, html):
		ext = self.get_ext(page['art'])
		if 'pages' not in ext:
			ext['pages'] = {}
		ext['pages'][page['url']] = html

	def put(self, article):
		if not self.is_done(article):
			for md5, page in article['pages'].iteritems():
				if page['status'] != 'done':
					task = {
						'_id': md5,
						'domain': article['domain'],
						'url': page['url'],
						'src': article['url'],
						'art': article['_id']
					}

					count = 0
					while not self.domains.fetch_page(task):
						self.master.wait(0)
						if count > 10:
							article['exc'] = 'DomainNotFound'
							article['last'] = time.time()
							self.articles.save(article, clean=True, update=True)
							self.log.warn('put page return False: %s' % page['url'])
							return
						count += 1

					self.log.debug('put page: %s' % page['url'])
			self.doing[article['_id']] = article
		else:
			self.finish(article)

	def fetch(self, page, res):
		if page['art'] not in self.doing:
			return

		article = self.doing[page['art']]
		article['last'] = time.time()
		self.articles.updates.add(article['_id'])

		tmp_page = article['pages'][page['_id']]
		if 'exc' not in res:
			tmp_page['path'] = res['path']
			tmp_page['status'] = 'done'
			tmp_page['last'] = time.time()
			self.update_ext(page, res['html'])
			self.log.debug('fetch page %s.' % page['url'])
			if self.is_done(article):
				del self.doing[article['_id']]
				self.finish(article)
				self.log.debug('fetch pages done from %s.' % article['_id'])
		else:
			tmp_page['status'] = 'error'
			tmp_page['last'] = time.time()
			article['exc'] = res['exc']
			del self.doing[article['_id']]
			self.error(article)
			self.log.warn('fetch page exception(%s).\narticle: %s\npage: %s'
				% (res['exc'], page['src'], page['url']))
