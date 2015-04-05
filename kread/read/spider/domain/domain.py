# coding: utf-8
import time
from .cates import Catecorys
from .tpls import Templates
from .arts import Articles
from .pages import Pages
from .imgs import Images


class Domain(object):

	def __init__(self, domains, domain):
		self.domains = domains
		self.master = domains.master
		self.log = domains.log
		self.domain = domain
		self.cates = Catecorys(self)
		self.tpls = Templates(self)
		self.arts = Articles(self)
		self.pages = Pages(self)
		self.imgs = Images(self)
		self.async = domains.master.async
		self.last = 0

	def sync(self, exit):
		self.cates.sync(exit)
		self.arts.sync(exit)

	def id(self):
		return self.domain['_id']

	def load(self):
		self.tpls.load()

	def back(self, start, end):
		if start < self.domain['last'] <= end:
			return {self.id():self.domain}
		return {}

	def update(self, domain):
		self.domain['name'] = domain['name']

	def new_arts(self, urls, src_type, task, last=0):
		num = 0
		for url in urls:
			num += self.arts.new(url, src_type, task['url'], task, last=last)
		self.domain['arts'] += 1
		self.domain['last'] = time.time()
		return num

	def get(self):
		self.last = now = time.time()
		cmds = [
			('cate', self.cates, [now]),
			('art', self.arts, [now]),
			('img', self.imgs, []),
			('page', self.pages, []),
			('art', self.arts, []),
		]

		for cmd, tasks, args in cmds:
			task = tasks.get(*args)
			if task:
				return cmd, task

		return None, None

	def cancel(self, cmd, task):
		cmds = {
			'cate': self.cates,
			'art': self.arts,
			'img': self.imgs,
			'page': self.pages,
		}
		if cmd in cmds:
			cmds[cmd].cancel(task)

	def fetch(self, cmd, task, res):
		cmds = {
			'cate': self.cates,
			'art': self.arts,
			'img': self.imgs,
			'page': self.pages,
		}

		if cmd in cmds:
			cmds[cmd].fetch(task, res)
			if 'exc' in res:
				self.master.counter.add('fetch_' + cmd + '_err')
				self.master.counter.add('fetch_err')
			else:
				self.master.counter.add('fetch_' + cmd)
				self.master.counter.add('fetch')
				self.master.counter.add('fetch_kb', len(res['html']) / 1024)
		else:
			self.log.warn('cmd %s not found on fetch of %s: %s.'
				% (cmd, self.id(), task['url']))

	def handle(self, cmd, task, res):
		cmds = {
			'cate': self.cates,
		}

		if cmd in cmds:
			cmds[cmd].handle(task, res)
		else:
			self.log.warn('cmd %s not found on handle of domain(%s): %s'
				% (cmd, self.id(), task['url']))

	def get_score(self):
		if not self.cates \
				and not self.arts \
				and not self.imgs \
				and not self.pages:
			return 2000000000

		if self.cates.wait > 0 and not self.arts and not self.imgs and not self.pages:
			score = self.cates.wait
		else:
			score = len(self.arts) * 0.01 + len(self.imgs) + len(self.pages)
			score = self.last - min(score, 300)

		return score

	def __repr__(self):
		return '<Domain %-20s(cates:%3d, arts:%4d, imgs:%4d(%4d), pages: %4d)>' % (
			self.id(), len(self.cates), len(self.arts), len(self.imgs), self.imgs.waits(), len(self.pages)
		)