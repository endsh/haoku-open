# coding: utf-8
import time
from deal import content4imgs, img2size
from spider.cmd import handle
from .base import ArtBase


class Art2MakeImg(ArtBase):

	def __init__(self, articles):
		super(Art2MakeImg, self).__init__(
			articles=articles,
			cmd='mea',
			ext_list=['imgs', 'content'],
		)

	def clean_ext(self, article):
		self.articles.clean_ext(article, 'content')

	def handle(self, key, res):
		if key not in self.doing:
			self.log.warn('article is not found in measure: %s' % key)
			return

		article = self.doing.pop(key)
		article['last'] = time.time()
		if 'exc' not in res:
			for md5, img in res['imgs'].iteritems():
				article['imgs'][md5]['width'] = img['width']
				article['imgs'][md5]['height'] = img['height']
			lab = lambda x: x[0] not in res['bads'] \
					and x[1]['path'] \
					and x[1]['width'] > x[1]['height'] \
					and x[1]['width'] >= 300 \
					and x[1]['height'] >= 250
			icons = dict(filter(lab, article['imgs'].iteritems()))
			if not icons:
				lab = lambda x: x[0] not in res['bads'] \
					and x[1]['path'] \
					and x[1]['width'] >= 300 \
					and x[1]['height'] >= 250
				icons = dict(filter(lab, article['imgs'].iteritems()))
			article['icons'] = icons
			self.finish(article, ext={'content':res['content']})
		else:
			article['exc'] = res['exc']
			self.error(article)
			self.log.warn('measure exception (%s) from %s.'
				% (res['exc'], article['url']))


@handle('mea')
def makeimg(handler, key, article, ext):
	if 'imgs' not in ext:
		ext['imgs'] = {}

	if 'content' not in ext or not ext['content']:
		ext['content'] = handler.text_file.get(article['content'])
		if not ext['content']:
			raise ValueError('load content failed.')
		ext['content'] = content.decode('utf-8')

	for md5, img in article['imgs'].iteritems():
		if md5 not in ext['imgs'] or not ext['imgs'][md5]:
			ext['imgs'][md5] = handler.image_file.get(img['path'])
			if not ext['imgs'][md5]:
				raise ValueError('%s load img failed.' % article['url'])

	res, image = {}, handler.mongo.image
	imgs, res['imgs'] = {}, {}
	for md5, img in ext['imgs'].iteritems():
		width, height = img2size(img)
		res['imgs'][md5] = {'width':width, 'height':height}

		row = image.find_one({'_id':md5})
		count = row['count'] if row is not None else 0
		imgs[article['imgs'][md5]['url']] = {
			'md5':md5, 
			'path':article['imgs'][md5]['path'], 
			'width':width, 
			'height':height,
			'count':count,
		}

	res['bads'], res['content'] = content4imgs(ext['content'], article['title'], imgs)
	return res