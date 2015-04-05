# coding: utf-8
import json
import time
from collections import defaultdict
from utils import url2filetype
from .base import ArtBase


class Art2Img(ArtBase):

	def __init__(self, articles):
		super(Art2Img, self).__init__(
			articles=articles,
			cmd='img',
		)
		self.domains = self.master.domains
		self.image = self.master.mongo.image

	def is_done(self, article):
		if not article['imgs']:
			return True

		for img in article['imgs'].itervalues():
			if img['status'] != 'done':
				return False
		return True

	def update_ext(self, img, html):
		ext = self.get_ext(img['art'])
		if 'imgs' not in ext:
			ext['imgs'] = {}
		ext['imgs'][img['_id']] = html

	def put(self, article):
		if not self.is_done(article):
			doing = False
			for md5, img in article['imgs'].iteritems():
				row = self.image.find_one({'_id':md5})
				if row is not None:
					img['status'] = 'done'
					img['path'] = row['path']
					img['last'] = time.time()
					self.image.update(
						{'_id':md5},
						{
							'$inc':{'count':1},
							'$addToSet':{'arts':article['_id']},
						},
					)
					continue
				if img['status'] != 'done':
					task = {
						'_id': md5,
						'domain': article['domain'],
						'url': img['url'],
						'src': article['url'],
						'art': article['_id']
					}

					count = 0
					while not self.domains.fetch_img(task):
						self.master.wait(0)
						if count > 10:
							article['exc'] = 'DomainNotFound'
							article['last'] = time.time()
							self.articles.save(article, clean=True, update=True)
							self.log.warn('put img return False: %s' % img['url'])
							return
						count += 1
					
					doing = True
					self.doing[article['_id']] = article
					self.log.debug('put img: %s' % img['url'])

			if not self.is_done(article):
				self.doing[article['_id']] = article
			else:
				self.finish(article)
		else:
			self.finish(article)

	def fetch(self, img, res):
		if img['art'] not in self.doing:
			self.log.warn('fetch img art not found: %s - %s' % (img['art'], img['url']))
			return

		article = self.doing[img['art']]
		article['last'] = time.time()
		self.articles.updates.add(article['_id'])

		tmp_img = article['imgs'][img['_id']]
		if 'exc' not in res:
			self.image.update(
				{'_id':img['_id']},
				{
					'$setOnInsert':{'path':res['path']}, 
					'$inc':{'count':1},
					'$addToSet':{'arts':article['_id']},
				},
				True
			)
			tmp_img['path'] = res['path']
			tmp_img['status'] = 'done'
			tmp_img['last'] = time.time()
			self.update_ext(img, res['html'])
			self.log.debug('fetch img %s.' % img['url'])
			if self.is_done(article):
				del self.doing[article['_id']]
				self.finish(article)
				self.log.debug('fetch imgs done from %s.' % article['_id'])
		else:
			tmp_img['status'] = 'error'
			tmp_img['last'] = time.time()
			article['exc'] = res['exc']
			del self.doing[article['_id']]
			self.error(article)
			self.log.warn('fetch img exception(%s).\narticle: %s\nimage: %s'
				% (res['exc'], img['src'], img['url']))

	def auto_finish(self):
		for id, art in self.doing.items():
			if self.is_done(art):
				del self.doing[id]
				self.finish(art)
				self.log.warn('article imgs is done: %s' % art['url'])

	def check(self):
		res = defaultdict(list)
		for id, art in self.doing.items():
			for md5, img in art['imgs'].iteritems():
				if img['status'] != 'done' \
						and not self.domains.is_fetching(md5) \
						and md5 not in self.domains.domains[art['domain']].imgs:
					res[id].append(img)
		return json.dumps(res, indent=4)