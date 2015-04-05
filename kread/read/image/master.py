#coding: utf-8
import re
import gevent
import hashlib
import time
import json
from utils import get, save_data, clean_doc, html2doc, u, PQDict, get_time
from utils.worker import GeventWorker
from conf import mongo_web
from db import MongoImage
from domain import Domain

def log(func):
	def wrapper(*args, **kw):
		# print 'call %s()...' % func.__name__
		return func(*args, **kw)
	return wrapper

o = {
	'_id':'http://www.youzi4.com/',
	're_cate':'href="(http:\/\/www\.youzi4\.com\/[^"]*?\/(list_.*?\.html)?)"',
	're_album':'href="(http:\/\/www\.youzi4\.com\/.*?\/\d+\.html)"',
	're_page':'href="(http:\/\/www\.youzi4\.com\/.*?\/\d+_\d+\.html)',
	're_title':'alt="(.*?)-.*?"',
	're_type':'<li><a class="active".*?>(.*?)<\/a><\/li>',
	're_image':'data-original="(http:\/\/img.d843.com\/uploads\/.*?\/\d+-.*?\.jpg)" id="bigimg"',
	'last':1410705419.978838,
	'status':'valid'
}
c = {
	'_id':'http://www.youzi4.com/', 
	'_type': '', 
	'domain':'http://www.youzi4.com/', 
	'state':0, 
	'status':'wait', 
	'last':1410705419.978838
}


class Master(GeventWorker):

	def __init__(self, count, conf):
		super(Master, self).__init__(count)

		db = MongoImage(conf, 'img')
		self.domain = db.domain
		self.catecory = db.catecory
		self.album = db.album
		self.file = db.file		
		self.sync_round = 90
		self.doing_round = (count + 1) / 2
		self.domains = PQDict(key=lambda x: x.value.domain['_id'])

		self.last = 0

		self.domain.save(o)
		self.catecory.save(c)
		
	def run(self):
		try:
			self.sync(init=True)
			while not self.is_exit():
				print "I'am coming"
				self.doing()
				self.clean()
				self.sync()
				self.wait(0.1)
		except KeyboardInterrupt:
			print 'keyboardInterrupt'
			self.sync(exit=True)

	
	def sync(self, init=False, exit=False):
		if not init and not exit \
				and self.sync_round > time.time() - self.last:
			return

		last = time.time()

		domains, cates, albums = {}, {}, {}

		if not init:
			for domain in self.domains:
				domains.update(domain.back_domain(self.last, last))
				cates.update(domain.back_cate(self.last, last))
				albums.update(domain.back_album(self.last, last))

		if not exit:
			self.load_domains(init, self.last, last, domains)
			self.load_cates(init, self.last, last, cates)
			self.load_albums(init, self.last, last, albums)

		for domain in domains.itervalues():
			self.domain.save(domain)

		for cate in cates.itervalues():
			self.catecory.save(cate)

		for album in albums.itervalues():
			album = album.copy()
			album['pages'] = json.dumps(album['pages'])
			album['imgs'] = json.dumps(album['imgs'])
			self.album.save(album)

	@log
	def doing(self):
		for x in xrange(self.doing_round):
			if self.is_exit():
				return
			domain = self.domains.get()
			task = domain.get()
			self.domains.put(domain)
			if not task:
				break
			self.do(task)

	@log
	def handle(self, index, task):
		try:
			index, task = task[0], task[1]
			url = task['_id']
			html = get(u(url))
			html = clean_doc(html2doc(html, url=url), return_html=True)
			if index == 'cate':
				self.domains[task['domain']].parse_cate(task, {'html':html})
			elif index == 'album':
				pass
			elif index == 'page':
				self.domains[task['domain']].parse_album(task, {'html':html})
		except KeyboardInterrupt:
			self.exit()


	@log
	def load_domains(self, init, start, end, domains):
		doc = {'status':'valid'} if init else {'last':{'$gt':start, '$lte':end}}
		for domain in self.domain.find(doc):
			self.add_domain(init, domain, domains)

	@log
	def load_cates(self, init, start, end, cates):
		doc = {'status':'wait'} if init else {'last':{'$gt':start, '$lte':end}}
		for cate in self.catecory.find(doc):
			if cate['domain'] in self.domains:
				self.domains[cate['domain']].add_cate(cate, cates)

	@log
	def load_albums(self, init, start, end, albums):
		doc = {'status':'wait'} if init else {'last':{'$gt':start, '$lte':end}}
		for album in self.album.find(doc):
			album['pages'] = json.loads(album['pages'])
			album['imgs'] = json.loads(album['imgs'])
			if album['domain'] in self.domains:
				self.domains[album['domain']].add_album(album, albums)

	@log
	def add_domain(self, init, domain, domains):
		_id = domain['_id']
		if domain['status'] == 'valid' and _id not in self.domains:
			domain = Domain(self, domain)
			if not init:
				domain.load()
			self.domains.put(domain)
		elif domain['status'] == 'invalid' and _id in self.domains:
			tmp = self.domains.pop(_id).domain
			if tmp['last'] < self.last:
				tmp['status'] = 'invalid'
				domains[_id] = tmp
  
  	@log
	def on_exit(self):
		self.sync(exit=True)


def main():
	master = Master(20, mongo_web)
	master.run()


if __name__ == '__main__':
	main()