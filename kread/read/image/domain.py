#coding: utf-8
import re
import time
import json
from utils import PQDict, get

def log(func):
	def wrapper(*args, **kw):
		# print 'call %s()...' % func.__name__
		return func(*args, **kw)
	return wrapper

def album_score(self):
	for x in self.value['pages'].itervalues():
		if x == 'wait':
			return 0
	return time.time()

class Domain(object):
	"""docstring for Domain"""
	def __init__(self, master, domain):
		super(Domain, self).__init__()
		self.master = master
		self.domain = domain
		self.re_cate 	= re.compile(self.domain['re_cate'])
		self.re_page 	= re.compile(self.domain['re_page'])
		self.re_album 	= re.compile(self.domain['re_album'])
		self.re_image 	= re.compile(self.domain['re_image'])
		self.re_title 	= re.compile(self.domain['re_title'])
		self.re_type 	= re.compile(self.domain['re_type'])
		self.cates = PQDict(key=lambda x:x.value['_id'], score=time.time)
		self.albums = PQDict(key=lambda x:x.value['_id'], score=album_score)
		self.doing = {}
		self.next = 0

	@log
	def load(self):
		doc = {'domain':self.domain['_id'], 'status':'wait'}
		cates = self.master.cate.find(doc)
		for cate in cates:
			self.add_cate(cate)

		albums = self.master.album.find(doc)
		for album in albums:
			album['pages'] = json.loads(album['pages'])
			album['imgs'] = json.loads(album['imgs'])
			self.add_album(album)

	@log
	def add_cate(self, cate, cates=None):
		_id = cate['_id']
		if cate['status'] == 'wait' \
				and _id not in self.cates \
				and _id not in self.doing:
			self.cates.put(cate)
		elif cate['status'] == 'invalid' and cates:
			tmp = None
			if _id in self.cates:
				tmp = self.cates.pop(_id)
			elif _id in self.doing:
				tmp = self.doing.pop(_id)

			if tmp and tmp['last'] > self.master.last:
				tmp['status'] = 'invalid'
				cates[_id] = tmp

	@log
	def add_album(self, album, albums=None):
		_id = album['_id']
		if album['status'] == 'wait' and _id not in self.albums:
			self.albums[_id] = album

		elif album['status'] == 'invalid' and _id in self.albums and albums:
			tmp = self.albums.pop(_id)
			if tmp and tmp['last'] > self.master.last:
				tmp['status'] = 'invalid'
				albums[_id] = tmp
 
 	@log
	def back_domain(self, start, end):
		domains = {}
		if start < self.domain['last'] <= end:
			domains[self.domain['_id']] = self.domain
		return domains

	@log
	def back_cate(self, start, end):
		cates = {}
		tmp = []
		for cate in self.cates.itervalues():
			if start < cate['last'] <= end:
				cates[cate['_id']] = cate
			tmp.append(cate)
		self.cates.extend(tmp)

		if cates:
			print('back %d cates from domain(%s).' % (len(cates), self.domain['_id']))

		for cate in self.doing.itervalues():
			if start < cate['last'] <= end and cate['_id'] in self.cates:
				cates[cate['_id']] = cate
		return cates

	@log
	def back_album(self, start, end):
		albums = {}
		tmp = []
		for album in self.albums.itervalues():
			if start < album['last'] <= end:
				albums[album['_id']] = album
			tmp.append(album)
		self.albums.extend(tmp)

		for album in self.doing.itervalues():
			if start < album['last'] <= end and album['_id'] in self.albums:
				albums[album['_id']] = album
		return albums

	@log
	def get(self):
		if not self.cates and not self.albums:
			return None
		while True:
			self.next += 1
			if self.next % 2 == 0 and len(self.albums) < 10:
				if self.cates :
					cate = self.cates.get()
					self.doing[cate['_id']] = cate
					return 'cate', cate

			if self.albums:
				album = self.albums.popitem()[1]
				for page, status in album['pages'].iteritems():
					if status == 'wait':
						album['pages'][page] = 'doing'
						self.doing[album['_id']] = album
						self.albums.put(album)
						return 'page', {'_id':page, 'domain':album['domain'], 'album':album['_id']}	

	@log
	def finish_cate(self, task):
		if task['_id'] in self.doing:
			task['status'] = 'done'
			self.master.catecory.save(task)
			del self.doing[task['_id']]
			if task['_id'] in self.cates:
				del self.cates[task['_id']]

	@log
	def finish_album(self, task):
		if task['album'] in self.albums:
			album = self.albums[task['album']]
			pages = album['pages']
			imgs = album['imgs']
			pages[task['_id']] = 'done'
			for value in pages.itervalues():
				if value in ['wait', 'doing']:
					return
			album = album.copy()
			album['pages'] = json.dumps(pages)
			album['imgs'] = json.dumps(imgs)
			album['status'] = 'done'
			self.master.album.save(album)
			if task['album'] in self.albums:
				del self.albums[task['album']]



	@log
	def parse_cate(self, task, result):
		html = result['html']
		cates = self.match(self.re_cate, html)
		albums = self.match(self.re_album, html)
		_type = self.search(self.re_type, html)
		for cate in cates:
			if cate not in self.cates and not self.master.catecory.find({'_id':cate}):
				# cha shu ju ku
				self.cates[cate] = {
					'_id':cate, 
					'_type': _type, 
					'domain':task['domain'], 
					'state':0, 
					'status':'wait', 
					'last':time.time()
				}

		for album in albums:
			if album not in self.albums:
				print album
				print '*' * 80
				self.albums[album] = {
						'_id':album, 
						'pages':{album:'wait'}, 
						'imgs':{} ,
						'domain':task['domain'],
						'cate': task['_id'],
						'status':'wait',
						'state':'valid', 
						'title':'',
						'last':time.time()}

		self.finish_cate(task)
	
	@log
	def parse_album(self, task, result):
		album_imgs = self.albums[task['album']]['imgs']
		album_pages = self.albums[task['album']]['pages']
		html = result['html']
		imgs = self.match(self.re_image, html)
		pages = self.match(self.re_page, html)

		title = self.albums[task['album']]['title']
		if not len(title):
			self.albums[task['album']]['title'] = self.search(self.re_title, html)

		if imgs:
			print imgs
			for img in imgs:
				if img not in album_imgs:
					album_imgs[img] = 'wait', ''
					content = get(img, allow_types='*/*', resp=True).content
					path = self.master.file.put(task['_id'], content, 'jpg')
					album_imgs[img] = 'done', path
		else:
			print 'imgs is None', imgs, task['_id']
			album_imgs[img] = 'wait'
		for page in pages:
			if page not in album_pages:
				album_pages[page] = 'wait'

		self.finish_album(task)

	@log
	def match(self, regx, html):
		""" need implements """
		return [x if type(x) in (str, unicode) else x[0] for x in regx.findall(html)]

	@log
	def search(self, regx, html, default=''):
		m = regx.search(html)
		return m.group(1) if m else default

	"""
		{
			'_id':'http://www.youzi4.com/',
			're_cate':'href="(http:\/\/www\.youzi4\.com\/[^"]*?\/(list_.*?\.html)?)"',
			're_album':'href="(http:\/\/www\.youzi4\.com\/.*?\/\d+\.html)"',
			're_page':'href="(http:\/\/www\.youzi4\.com\/.*?\/\d+_\d+\.html)',
			're_title':'alt="(.*?)-.*?"',
			're_type':'<li><a class="active".*?>(.*?)<\/a><\/li>',
			're_image':'data-original="(http:\/\/img.d843.com\/uploads\/.*?\/\d+-.*?\.jpg)"',
			'last':1410705419.978838,
			'status':'valid'
		}
	"""

	"""
		{
			'_id':'http://www.youzi4.com/', 
			'_type': '', 
			'domain':'http://www.youzi4.com/', 
			'state':0, 
			'status':'wait', 
			'last':1410705419.978838
		}

	"""


