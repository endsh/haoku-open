# coding: utf-8
import time
import redis
import hashlib
from collections import OrderedDict
from utils import PQDict, get_domain, atime
from .domain import Domain


class Domains(object):

	def __init__(self, master):
		self.master = master
		self.log = master.log
		self.domain = master.mongo.domain
		self.catecory = master.mongo.catecory
		self.template = master.mongo.template
		self.article = master.mongo.spider_article
		self.exc_article = master.mongo.spider_exc
		self.html_file = master.mongo.html_file
		self.url_redis = redis.Redis(**master.conf.redis_url)
		self.domains = PQDict(key=lambda x: x.value.domain['_id'])
		self.fetching = dict()
		self.waiting = OrderedDict()
		self.doing = dict()
		self.sync_round = 1800
		self.last = -1

		master.fetch_adapter.register(['cate','art','page','img'], 
			self.fetch_get, self.fetch, self.fetch_cancel)
		master.handle_adapter.register(['cate'], 
			self.handle_get, self.handle, self.handle_cancel)

	@property
	def counter(self):
		res = {
			'fetch':len(self.fetching), 
			'domain_wait':len(self.waiting),
			'domain_doing':len(self.doing),
			'fetch_cate':0,
			'fetch_art':0,
			'fetch_img':0,
			'fetch_page':0,
		}
		for cmd, _ in self.fetching.itervalues():
			res['fetch_' + cmd] += 1
		return res

	def is_fetching(self, key):
		return key in self.fetching

	def is_doing(self, key):
		return key in self.fetching \
			or key in self.waiting \
			or key in self.doing

	def sync(self, quit=False):
		self.sync_last(quit)
		self.sync_other(quit)

	def sync_last(self, quit):
		if not quit and self.sync_round > time.time() - self.last:
			return

		last = time.time()
		domains, tpls = {}, {}

		for domain in self.domains:
			domains.update(domain.back(self.last, last))
			tpls.update(domain.tpls.back(self.last, last))

		if not quit:
			self.load_domains(self.last, last)
			self.load_tpls(self.last, last)

		for domain in domains.itervalues():
			self.domain.save(domain)
		for tpl in tpls.itervalues():
			self.template.save(tpl)

		self.last = last

	def sync_other(self, quit):
		for domain in self.domains:
			domain.sync(quit)
		self.domains.heapify()

	def load_domains(self, start, end):
		doc = {'status':'common', 'last':{'$gt':start, '$lte':end}}
		domains = self.domain.find(doc)
		for domain in domains:
			if domain['_id'] not in self.domains:
				xdomain = Domain(self, domain)
				self.domains.put(xdomain)
				if start > 0:
					xdomain.load()
			else:
				self.domains[domain['_id']].update(domain)
		if domains.count() > 0:
			self.log.info('load %d domains.' % domains.count())

	def load_tpls(self, start, end):
		doc = {'status':'common', 'last':{'$gt':start, '$lte':end}}
		tpls = self.template.find(doc)
		for tpl in tpls:
			with self.domains.get2do(tpl['domain']) as domain:
				domain.tpls.put(tpl)

		if tpls.count > 0:
			self.log.info('load %d tpls.' % tpls.count())

	def add_url(self, key, domain):
		return self.url_redis.sadd(domain, key)

	def has_url(self, key, domain):
		return self.url_redis.sismember(domain, key)

	def selector(self, domain, tpl):
		if domain in self.domains:
			return self.domains[domain].tpls.selector(tpl)
		return {}

	def new_arts(self, article, urls):
		with self.domains.get2do(article['domain']) as domain:
			return domain.new_arts(urls, 'art', article)
		return 0

	def fetch_page(self, page):
		with self.domains.get2do(page['domain']) as domain:
			return domain.pages.put(page)
		return False

	def fetch_img(self, img):
		with self.domains.get2do(img['domain']) as domain:
			return domain.imgs.put(img)
		return False

	def new_handle(self, key, value):
		self.waiting[key] = value

	def quit(self):
		for cmd, task in self.fetching.itervalues():
			self.domains[task['domain']].cancel(cmd, task)
		self.fetching.clear()

		for cmd, task, _ in self.waiting.itervalues():
			self.domains[task['domain']].cancel(cmd, task)
		self.waiting.clear()

		for cmd, task in self.doing.itervalues():
			self.domains[task['domain']].cancel(cmd, task)
		self.doing.clear()

	def fetch_get(self, count):
		tasks = []
		if not self.domains:
			return tasks

		null = 0
		for _ in xrange(count):
			cmd, task = None, None
			with self.domains.get2do() as domain:
				cmd, task = domain.get()

			if not task:
				null += 1
				if null >= 5:
					break
				self.domains.heapify()
				continue
				
			tasks.append({'key':task['_id'], 'cmd':cmd, 'info':task})
			self.fetching[task['_id']] = (cmd, task)

		return tasks

	def fetch_cancel(self, key, cmd):
		if key in self.fetching:
			cmd, task = self.fetching.pop(key)
			with self.domains.get2do(task['domain']) as domain:
				domain.cancel(cmd, task)

	def fetch(self, key, cmd, res):
		if key in self.fetching:
			cmd, task = self.fetching.pop(key)
			with self.domains.get2do(task['domain']) as domain:
				domain.fetch(cmd, task, res)
				
	def handle_get(self, count, **kwargs):
		tasks = []
		for _ in xrange(min(len(self.waiting), count)):
			cmd, task, ext = self.waiting.popitem()[1]
			tasks.append({'key':task['_id'], 'cmd':cmd, 'info':task, 'ext':ext})
			self.doing[task['_id']] = (cmd, task)
		return tasks

	def handle_cancel(self, key, cmd):
		if key in self.doing:
			cmd, task = self.doing.pop(key)
			with self.domains.get2do(task['domain']) as domain:
				domain.cancel(cmd, task)

	def handle(self, key, cmd, res):
		if key in self.doing:
			cmd, task = self.doing.pop(key)
			with self.domains.get2do(task['domain']) as domain:
				domain.handle(cmd, task, res)