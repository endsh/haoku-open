# coding: utf-8
import json


class ArtBase(object):

	def __init__(self, articles, cmd, ext_list=[]):
		self.articles = articles
		self.master = articles.master
		self.log = articles.log
		self.doing = dict()
		self.cmd = cmd
		self.next = ''
		self.articles.register(cmd, self)
		self.ext_list = ext_list

	@property
	def version(self):
		return self.articles.get_version(self.cmd)

	def __contains__(self, key):
		return key in self.doing

	def __len__(self):
		return len(self.doing)

	def cancel_on_exit(self):
		if self.cmd in ['page', 'img']:
			for article in self.doing.itervalues():
				self.articles.save(article, clean=True)
		else:
			for article in self.doing.itervalues():
				self.articles.put(article)
		self.doing.clear()
		self.log.info('%s cancel on exit ...' % self.cmd)

	def cancel(self, key):
		if key in self.doing:
			article = self.doing.pop(key)
			self.articles.put(article)

	def get_ext(self, key):
		return self.articles.get_ext(key)

	def update_ext(self, key, ext):
		self.get_ext(key).update(ext)

	def make_ext(self, article):
		pass

	def clean_ext(self, article):
		pass

	def do(self, article):
		self.doing[article['_id']] = article
		ext = self.get_ext(article['_id'])
		return dict((k, ext[k]) for k in filter(lambda x: x in ext, self.ext_list))

	def handle(self, key, res):
		raise NotImplementedError

	def finish(self, article, ext=None):
		self.clean_ext(article)
		article['v'][self.cmd] = self.version
		if self.next:
			article['v'][self.next] = 0
			
		self.articles.put(article, ext=ext, update=True)
		self.master.counter.add('article_%s' % self.cmd)
		self.master.counter.add('article')

	def error(self, article):
		self.articles.save(article, clean=True, update=True)
		self.master.counter.add('article_%s_err' % self.cmd)
		self.master.counter.add('article_err')

	def dump(self):
		return self.doing