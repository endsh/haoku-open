# coding: utf-8
import time
import pymongo
import redis
from collections import OrderedDict
from utils import PQDict
from .article import Art2Urls, Art2Extract, Art2Page, Art2Merger
from .article import Art2Img, Art2MakeImg, Art2Sim, Art2Segment, Art2MakeTag


class Articles(object):

	def __init__(self, master):
		self.master = master
		self.domains = master.domains
		self.async = master.async
		self.log = master.log
		self.spider_article = master.mongo.spider_article
		self.spider_exc = master.mongo.spider_exc
		self.word_file = master.mongo.word_file
		self.html_file = master.mongo.html_file
		self.text_file = master.mongo.text_file
		self.article = master.mongo.article
		self.image_file = master.mongo.image_file
		self.redis_word = master.redis_word
		self.redis_tag = master.redis_tag

		self.waiting = PQDict(
			key=lambda x: x.value['_id'],
			score=lambda x: -x.value['pubtime'],
		)
		self.waiting_seg = PQDict(
			key=lambda x: x.value['_id'],
			score=lambda x: -x.value['pubtime'],
		)
		self.starts = dict()
		self.updates = set()
		self.dones = set()
		self.extends = dict()
		self.cmds = OrderedDict()
		self.doc = {'f':True}
		self.previous = None
		self.backing = False
		self._len = 0
		self._last = 0

		self.version = {
			'ext': 0.1,
			'url': 0.1,
			'pag': 0.1,
			'mer': 0.1,
			'img': 0.1,
			'mea': 0.1,
			'sim': 0.1,
			'seg': 0.2,
		}

		self.ext_arts = Art2Extract(self)
		self.url_arts = Art2Urls(self)
		self.pag_arts = Art2Page(self)
		self.mer_arts = Art2Merger(self)
		self.img_arts = Art2Img(self)
		self.mea_arts = Art2MakeImg(self)
		self.sim_arts = Art2Sim(self)
		self.seg_arts = Art2Segment(self)
		self.common = 20000
		self.limit = 10000
		self.null = False
		self.last = 0
		self.cnt = 0
		self.load_num = 0

		if self.master.conf.RELEASE == False:
			self.common = 5000
			self.limit = 3000 

		self.update_last = 0

		self.set_adapter(master.handle_adapter)

	@property
	def counter(self):
		res = {'article':0}
		for cmd, instance in self.cmds.iteritems():
			res['article_' + cmd] = len(instance)
			res['article'] += res['article_' + cmd];

		res['article_wait'] = len(self.waiting)
		res['article_load'] = self.load_num
		return res

	def doing_len(self):
		if time.time() - self._last < 5:
			return self._len

		self._last = time.time()

		_len = len(self.waiting)
		for instance in self.cmds.itervalues():
			_len += len(instance)
		self._len = _len
		return _len

	def register(self, cmd, instance):
		self.cmds[cmd] = instance
		if self.previous is not None:
			self.previous.next = cmd
		self.previous = instance

	def set_adapter(self, adapter):
		cmds = []
		for cmd in self.cmds:
			if cmd not in ['pag', 'img']:
				cmds.append(cmd)

		adapter.register(cmds, self.get, self.handle, self.cancel, extend=True)

	def update(self):
		self.img_arts.auto_finish()
		if time.time() - self.update_last > 300:
			self.update_last = time.time()

	def get_version(self, cmd):
		return self.version.get(cmd, 0)

	def new_version(self):
		return dict((x, 0) for x in self.cmds.iterkeys())

	def is_doing(self, key):
		for instance in self.cmds.itervalues():
			if key in instance:
				return True
		return False

	def is_waiting(self, key):
		return key in self.waiting or key in self.waiting_seg

	def __contains__(self, key):
		return self.is_waiting(key) or self.is_doing(key)

	def put(self, article, ext=None, update=False):
		if article['_id'] in self:
			return 0

		# if article['_id'] in self.dones:
		# 	print article['_id'], article['url'], article['v']
		# 	return 0

		if update:
			self.updates.add(article['_id'])

		article['version'] = sum(article['v'].itervalues())

		self.update_ext(article, ext)

		for cmd, instance in self.cmds.iteritems():
			if article['v'][cmd] < self.version[cmd]:
				if cmd == 'pag':
					self.pag_arts.put(article)
				elif cmd == 'img':
					self.img_arts.put(article)
				else:
					if cmd == 'mer' and not article['pages']:
						self.mer_arts.finish(article)
						return 1

					if cmd == 'mea' and not article['imgs']:
						self.mea_arts.finish(article)
						return 1

					instance.make_ext(article)
					if cmd == 'seg':
						self.waiting_seg.put(article)
					else:
						self.waiting.put(article)
				return 1

		self.cnt += 1
		self.dones.add(article['_id'])
		self.save(article, clean=True, update=update)
		self.log.info('article(%d): %s' % (self.cnt, article['url']))
		return 0

	def save(self, article, clean=False, update=False):
		res = 0
		if update == True or article['_id'] in self.updates:
			if article['_id'] in self.updates:
				self.updates.remove(article['_id'])
			if 'exc' in article:
				self.spider_exc.save(article)
				self.spider_article.remove({'_id':article['_id']})
			else:
				self.spider_article.save(article)
			res = 1

		if clean == True:
			ext = self.clean_ext(article)
			if res == 1 and 'content' in ext:
				self.text_file.put(article['content'], ext['content'].encode('utf-8'))

		return res

	def update_ext(self, article, ext):
		if ext is not None:
			if article['_id'] not in self.extends:
				self.extends[article['_id']] = ext
			else:
				self.extends[article['_id']].update(ext)

	def clean_ext(self, article, *args):
		if not args:
			return self.extends.pop(article['_id'], None)
		if article['_id'] not in self.extends:
			return None
		ext = self.extends[article['_id']]
		self.extends[article['_id']] = dict((x, ext[x]) for x in args if x in ext)
		return self.extends[article['_id']]

	def get_ext(self, key):
		if key not in self.extends:
			self.extends[key] = {}
		return self.extends[key]

	def sync(self, quit=False):
		if quit:
			self.back_on_quit()
		else:
			if len(self.waiting) >= self.common * 2:
				self.back()
				self.null = False
			elif self._len <= self.common and (not self.null
					or time.time() > self.last + self.domains.sync_round):
				self.load()
				self.last = time.time()

	def load(self):
		self.log.info('articles load start ...')
		num = 0
		keys = [
			('pubtime', pymongo.DESCENDING),
		]
		version = sum(self.version.itervalues())
		# if self.version['tag'] > 0.4:
		# 	version -= 0.4
		# self.doc['version'] = {'$lt':version}
		self.doc['version'] = 0

		articles = self.spider_article.find(self.doc)
		
		articles.sort(keys).limit(self._len + self.limit)
		#articles.limit(self._len + self.limit)

		limit = self.limit
		for article in articles:
			if self.put(article):
				num += 1
				self.load_num += 1
			if num >= limit:
				break

		self.null = True if num == 0 else False
		self.log.info('load %d/%d articles to handle.'
			% (num, len(self.waiting)))

	def back(self):
		if self.backing == True:
			return

		self.backing = True
		count = len(self.waiting)
		for article in self.waiting.tail(self.limit):
			self.async.do(self.save, article, clean=True)
		self.log.info('back %d/%d articles from handle.' % (limit, count))

		self.backing = False

	def back_on_quit(self):
		count, num = len(self.waiting), 0
		for article in self.waiting.itervalues():
			num += self.save(article, clean=True)
		self.log.info('back %d/%d articles from handle on exit.' % (num, count))

	def quit(self):
		for instance in self.cmds.itervalues():
			instance.cancel_on_exit()

	def get(self, count, seg=False):
		tasks = []
		waiting = self.waiting_seg if seg == True else self.waiting
		for _ in xrange(count):
			try:
				article = waiting.get()
			except KeyError:
				break
			for cmd, instance in self.cmds.iteritems():
				if article['v'][cmd] < self.version[cmd]:
					ext = instance.do(article)
					tasks.append({'key':article['_id'], 'cmd':cmd, 'info':article, 'ext':ext})
					break
		return tasks

	def handle(self, key, cmd, res):
		if cmd in self.cmds:
			self.cmds[cmd].handle(key, res)
		else:
			self.log.warn('cmd (%s) not found of key: %s.' % (cmd, key))

	def cancel(self, key, cmd):
		if cmd in self.cmds:
			self.cmds[cmd].cancel(key)