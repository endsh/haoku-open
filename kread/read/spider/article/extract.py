# coding: utf-8
import time
import hashlib
from deal import html2article
from utils import get_time, url2time, unicode2hash
from spider.cmd import handle
from .base import ArtBase


class Art2Extract(ArtBase):

	def __init__(self, articles):
		super(Art2Extract, self).__init__(
			articles=articles,
			cmd='ext',
			ext_list=['html', 'selector'],
		)
		self.domains = self.master.domains

	def make_ext(self, article):
		ext = self.get_ext(article['_id'])
		if 'selector' not in ext or not ext['selector']:
			ext['selector'] = self.articles.domains.selector(
				article['domain'], article['tpl'])

	def handle(self, key, res):
		if key not in self.doing:
			self.log.warn('article is not found in extract: %s' % key)
			return

		article = self.doing.pop(key)
		article['last'] = time.time()
		if 'exc' not in res:
			art = res['article']
			article['title'] = art['title']
			article['content'] = 'spider_%s.txt' % article['_id']
			article['pubtime'] = art['pubtime']
			if art['src_name']:
				article['src_name'] = art['src_name']
				article['src_link'] = art['src_link']
			self.merger_pages(article, art['pages'])
			self.merger_imgs(article, art['imgs'])
			self.finish(article, {'content':art['content']})
			self.log.debug('extract: %s\n%s' % (article['url'], article['title']))
		else:
			article['exc'] = res['exc']
			self.error(article)
			self.log.warn('extract exception (%s) from %s.'
				% (res['exc'], article['url']))

	def merger_pages(self, article, pages):
		tmp_pages = article['pages']
		article['pages'] = {}
		for page in pages:
			md5 = hashlib.md5(page.encode('utf-8')).hexdigest()
			xlong = unicode2hash(page)
			self.domains.add_url(xlong, article['domain'])
			if md5 in tmp_pages:
				article['pages'][md5] = tmp_pages[md5]
			else:
				article['pages'][md5] = {
					'url': page,
					'path': '',
					'status': 'wait',
					'last': time.time(),
				}

		for md5, page in tmp_pages.iteritems():
			if md5 not in article['pages'] and page['status'] == 'done':
				self.articles.html_file.remove(page['path'])

	def merger_imgs(self, article, imgs):
		tmp_imgs = article['imgs']
		article['imgs'] = {}
		for img in imgs:
			md5 = hashlib.md5(img.encode('utf-8')).hexdigest()
			if md5 in tmp_imgs:
				article['imgs'][md5] = tmp_imgs[md5]
			else:
				article['imgs'][md5] = {
					'url': img,
					'path': '',
					'width': 0,
					'height': 0,
					'status': 'wait',
					'last': time.time(),
				}
				
		for md5, img in tmp_imgs.iteritems():
			if md5 not in article['imgs'] and img['status'] == 'done':
				self.articles.image_file.remove(img['path'])


@handle('ext')
def extract(handler, key, info, ext):
	if 'html' not in ext or not ext['html']:
		if not info['html']:
			raise ValueError('info html is None')
		ext['html'] = handler.html_file.get(info['html'])
		handler.log.info('load html: %s - %d' % (info['html'], len(ext['html'])))
		if not ext['html']:
			raise ValueError('load html failed.')

	article = html2article(ext['html'], info['url'], **ext['selector'])
	if not article:
		raise ValueError('article not found.')

	article['pages'] = filter(lambda x: x != info['url'], article['pages'])

	if article['pubtime']:
		pubtime = get_time(article['pubtime'])
		if pubtime < 946656000:
			pubtime = url2time(info['url'])
		article['pubtime'] = pubtime
	else:
		article['pubtime'] = url2time(info['url'])

	if article['pubtime'] > time.time():
		article['pubtime'] = info['created'] - 86400 * 7

	return {'article':article}
