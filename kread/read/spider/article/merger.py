# coding: utf-8
import time
import hashlib
from deal import ArticleMerger
from spider.cmd import handle
from .base import ArtBase


class Art2Merger(ArtBase):

	def __init__(self, articles):
		super(Art2Merger, self).__init__(
			articles=articles,
			cmd='mer',
			ext_list=['html', 'selector', 'pages'],
		)

	def make_ext(self, article):
		ext = self.get_ext(article['_id'])
		if 'selector' not in ext or not ext['selector']:
			ext['selector'] = self.articles.domains.selector(
				article['domain'], article['tpl'])

	def clean_ext(self, article):
		self.articles.clean_ext(article, 'content')

	def handle(self, key, res):
		if key not in self.doing:
			self.log.warn('article is not found in merger: %s' % key)
			return

		article = self.doing.pop(key)
		article['last'] = time.time()
		if 'exc' not in res:
			self.merger_imgs(article, res['imgs'])
			self.finish(article, ext={'content':res['content']})
		else:
			article['exc'] = res['exc']
			self.error(article)
			self.log.warn('merger exception (%s) from %s.'
				% (res['exc'], article['url']))

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


@handle('mer')
def merger(handler, key, article, ext):
	if 'html' not in ext or not ext['html']:
		ext['html'] = handler.html_file.get(article['html'])
		if not ext['html']:
			raise ValueError('%s load html failed.' % article['url'])

	if 'pages' not in ext:
		ext['pages'] = {}

	for page in article['pages'].itervalues():
		if page['url'] not in ext['pages'] or not ext['pages'][page['url']]:
			ext['pages'][page['url']] = handler.html_file.get(page['path'])
			if not ext['pages'][page['url']]:
				raise ValueError('%s load page html failed.' % page['url'])

	pages = ext['pages']
	pages[article['url']] = ext['html']
	mer = ArticleMerger(article['url'], article['title'], pages, **ext['selector'])
	return {'content':mer.content, 'imgs':mer.imgs}