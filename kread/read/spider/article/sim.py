# coding: utf-8
import sys
import time
from simhash import Simhash
from utils import html2text
from spider.cmd import handle
from .base import ArtBase


class Art2Sim(ArtBase):

	def __init__(self, articles):
		super(Art2Sim, self).__init__(
			articles=articles,
			cmd='sim',
			ext_list=['content'],
		)

	def handle(self, key, res):
		if key not in self.doing:
			self.log.warn('article is not found in simhash: %s' % key)
			return

		article = self.doing.pop(key)
		article['last'] = time.time()
		if 'exc' not in res:
			article['sim'] = res['sim']
			self.finish(article)
		else:
			article['exc'] = res['exc']
			self.error(article)
			self.log.warn('simhash exception (%s) from %s.'
				% (res['exc'], article['url']))


@handle('sim')
def sim(handler, key, article, ext):
	mongo = handler.mongo
	mongo.sim.unset(article['_id'], article['sim'])

	if 'content' not in ext or not ext['content']:
		ext['content'] = handler.text_file.get(article['content'])
		if not ext['content']:
			raise ValueError('load content failed.')
		ext['content'] = content.decode('utf-8')

	text = article['title'] + html2text(ext['content'])
	num = Simhash(text).value - sys.maxint
	near = mongo.sim.near(num)

	key = mongo.sim.save(article['_id'], num, near)
	return {'sim':key}
