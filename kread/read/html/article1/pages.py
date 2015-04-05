# coding: utf-8
import re
from utils import url2filetype
from .base import BaseParser

__all__ = [
	'PagesParser',
]


class PagesParser(BaseParser):

	def parse(self):
		file_type = url2filetype(self.article.url)
		if not file_type:
			return {'urls':[]}
		pages = set([self.article.url])
		prefix = self.article.url[:-len(file_type) - 1]
		if re.match('.*[_\-]\d$', prefix):
			prefix = self.article.url[:-len(file_type) - 3]
		prefix_len = len(prefix)

		for node in self.article.doc.iter('a'):
			href = node.get('href').strip() if node.get('href') else None
			if href and len(href) > prefix_len + 2 \
					and href[:prefix_len] == prefix:
				href = href.split('#')[0].split('?')[0]
				pages.add(href)

		pages = list(pages)
		if len(pages) == 1:
			pages = []
		return {'urls': pages}