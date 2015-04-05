# coding: utf-8
import time
import hashlib
from utils import html2urls
from spider.cmd import handle
from .base import ArtBase


class Art2Urls(ArtBase):

	def __init__(self, articles):
		super(Art2Urls, self).__init__(
			articles=articles,
			cmd='url',
			ext_list=['html'],
		)
		self.domains = self.master.domains

	def clean_ext(self, article):
		if not article['pages']:
			self.articles.clean_ext(article, 'content')

	def handle(self, key, res):
		if key not in self.doing:
			self.log.warn('article is not found in extract: %s' % key)
			return

		article = self.doing.pop(key)
		article['last'] = time.time()
		if 'exc' not in res:
			num = self.domains.new_arts(article, res['urls'])
			self.finish(article)
			self.log.debug('parse %s arts from article: %s' % (num, article['url']))
		else:
			article['exc'] = res['exc']
			self.error(article)
			self.log.info('parse arts exception (%s) from %s.'
				% (res['exc'], article['url']))


@handle('url')
def art2urls(handler, key, info, ext):
	if 'html' not in ext or not ext['html']:
		ext['html'] = handler.html_file.get(info['html'])
		if not ext['html']:
			raise ValueError('%s load html failed.' % info['url'])
	return {'urls':html2urls(ext['html'], info['url'], name=False)}
