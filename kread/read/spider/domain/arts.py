# coding: utf-8
import re
import time
import pymongo
import hashlib
from utils import PQDict, url2tpl, unicode2hash

re_date = re.compile('[\/\-_](20\d{2})[\/\-_]?(0\d|1[0-2])[\/\-_]?(0[1-9]|[12]\d|3[01])?[\/\-_]')


class Articles(object):

	def __init__(self, domain):
		self.domain = domain
		self.domains = domain.domains
		self.articles = domain.domains.master.articles
		self.article = domain.domains.article
		self.exc_article = domain.domains.exc_article
		self.log = domain.log
		self.queue = PQDict(
			key=lambda x: x.value['_id'],
			score=lambda x: -x.value['pubtime'],
		)
		self.updates = set()
		self.full = 2000
		self.common = 1000
		self.limit = 100
		self.null = False
		self.next = 0
		self.last = 0

		self.xcount = 0
		self.xlast = 0

	def __contains__(self, key):
		return key in self.queue or self.domains.is_fetching(key)

	def __nonzero__(self):
		return len(self.queue) > 0

	def __len__(self):
		return len(self.queue)

	def put(self, article, update=False):
		if article['_id'] in self:
			return 0

		if update == True:
			self.updates.add(article['_id'])

		if self.next < article['pubtime']:
			self.next = article['pubtime']

		self.queue.put(article)

		return 1

	def save(self, article, update=False):
		if update == True or article['_id'] in self.updates:
			if article['_id'] in self.updates:
				self.updates.remove(article['_id'])
			if 'exc' in article:
				self.exc_article.save(article)
			else:
				self.article.save(article)
			return 1
		return 0

	def new(self, url, src_type, src, task, last=0):
		key = hashlib.md5(url.encode('utf-8')).hexdigest()
		xlong = unicode2hash(url)
		tpl = url2tpl(url)
		if tpl not in self.domain.tpls \
				or key in self \
				or self.domains.add_url(xlong, self.domain.id()) == 0:
			return 0

		article = {
			'_id': key,
			'id': '',
			'long': xlong,
			'url': url,
			'domain': self.domain.id(),
			'tpl': tpl,
			'src_type': src_type,
			'src': src,
			'html': '',
			'title': '',
			'pages': {},
			'imgs': {},
			'icons': {},
			'tags': [],
			'sim': False,
			'f': False,
			'version': 0,
			'v': self.articles.new_version(),
			'created': time.time(),
			'last': time.time(),
		}

		if src_type == 'cate':
			article['src_link'] = task['url']
			article['src_name'] = task['name']
			if last > 0:
				article['pubtime'] = last
			else:
				article['pubtime'] = time.time() - 86400 * 60
		else:
			article['src_link'] = self.domain.domain['link']
			article['src_name'] = self.domain.domain['name']
			article['pubtime'] = task['pubtime'] - 86400 * 15

		article['pubtime'] = self.get_pubtime(article)

		if self.next < article['pubtime']:
			self.next = article['pubtime']

		self.updates.add(article['_id'])
		self.queue.put(article)
		return 1

	def sync(self, exit):
		if exit:
			self.back_on_exit()
		else:
			if len(self.queue) >= self.full * 2:
				self.back()
			elif len(self.queue) <= self.limit and (not self.null
					or time.time() >= self.last + self.domains.sync_round):
				self.load()
				self.last = time.time()

	def load(self):
		doc = {
			'domain': self.domain.id(),
			'f': False,
		}
		articles = self.article.find(doc)
		articles.sort('pubtime', pymongo.DESCENDING).limit(self.common)
		num = 0
		for article in articles:
			num += self.put(article)

		self.null = True if num == 0 else False
		self.log.info('load %d/%d articles from %s to fetch.'
			% (num, min(articles.count(), self.common), self.domain.id()))

	def back(self):
		count = len(self.queue)
		limit = count - self.common * 2
		for article in self.queue.tail(limit):
			self.save(article)
		self.null = False
		self.log.info('back %d/%d articles from %s.'
			% (limit, count, self.domain.id()))

	def back_on_exit(self):
		count, num = len(self.queue), 0
		for article in self.queue.itervalues():
			num += self.save(article)
		self.log.info('back %d/%d articles from %s on exit.'
			% (num, count, self.domain.id()))

	def get(self, now=0):
		if self.queue:
			if now > 0:
				today = now // 86400 * 86400
				if self.next == 0 or today < self.next <= now:
					article = self.queue.get()
					self.next = article['pubtime']
					if today < self.next <= now:
						return article
					self.queue.put(article)
			else:
				# if self.articles.doing_len() > 5000:
				# 	if self.xcount >= 50 and time.time() - self.xlast < 5:
				# 		return None

				# 	if time.time() - self.xlast >= 5:
				# 		self.xcount = 0
				# 		self.xlast = time.time()

				# self.xcount += 1
				return self.queue.get()

	def cancel(self, article):
		self.queue.put(article)

	def fetch(self, article, res):
		article['last'] = time.time()
		if 'exc' not in res:
			article['html'] = res['path']
			article['f'] = True
			self.save(article, update=True)

			ext = {
				'html': res['html'],
				'selector': self.domain.tpls.selector(article['tpl']),
			}
			if self.articles._len < 30000 or time.time() - article['pubtime'] < 86400:
				self.articles.put(article, ext=ext)
			self.log.debug('fetch article %s.' % article['url'])
		else:
			article['exc'] = res['exc']
			self.save(article, update=True)
			self.log.warn('fetch article except(%s): %s.'
				% (res['exc'], article['url']))

	def get_pubtime(self, article):
		now = time.time()
		match = re_date.search(article['url'])
		if match:
			year, month, day = match.group(1), match.group(2), match.group(3)

			if not day:
				day = '01'

			try:
				return min(now, time.mktime(time.strptime(
					'%s-%s-%s' % (year, month, day), "%Y-%m-%d")) + 43200)
			except:
				pass

		if article['pubtime']:
			return article['pubtime']

		return now - (86400 * 60)