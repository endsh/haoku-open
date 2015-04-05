# coding: utf-8
from utils import tag2text
from .base import BaseParser, ArticleNotFound, CATES
from ..doc import selector

__all__ = [
	'TitleParser',
]


class TitleParser(BaseParser):

	def get_title_text(self):
		title = tag2text(self.article.doc, 'meta', property='og:title')
		if not title:
			title = tag2text(self.article.doc, 'title').strip()
			if not title:
				raise ArticleNotFound('title is None.')

			domain_name = self.options.get('domain_name')
			if domain_name:
				if domain_name.endswith(u'网'):
					domain_text = domain_name[:-1]
				else:
					domain_text = domain_name
				words = []
				for spliter in '_|-':
					if spliter in title:
						words = title.split(spliter)
						break
				
				new = []
				for word in words:
					if domain_name in word \
							or domain_text in word \
							or len(word) >= 2 and word[:2] in CATES \
							or len(word) >= 2 and word[-2:] in CATES:
						continue
					new.append(word)
				title = spliter.join(new)
		return title

	def parse(self):
		title = self.get_title_text()

		if self.options.get('title_selector', ''):
			heads = []
			for node in self.article.select(self.options['title_selector']):
				heads.append(node)
			if len(heads) == 1:
				return self.node2title(heads[0])

		maxlen, node = 0, None
		body = self.article.doc.find('body')
		if body is None:
			raise ArticleNotFound('article doc body is None.')

		for child in body.iter():
			if child.text and child.text.strip():
				text = child.text.strip()
				if len(text) >= maxlen and (title.startswith(text) or title.endswith(text)):
					if len(text) > maxlen or child.tag in 'h1|h2|h3|h4|h5|h6':
						maxlen, node = len(text), child
			if child.tail and child.tail.strip() and child.getparent() is not None:
				text = child.tail.strip()
				if len(text) > maxlen and (title.startswith(text) or title.endswith(text)):
					if len(text) > maxlen or child.getparent().tag in 'h1|h2|h3|h4|h5|h6':
						maxlen, node = len(text), child.getparent()
		return self.node2title(node, title)

	def node2title(self, node=None, title=''):
		if node is None or title == '':
			raise ArticleNotFound('node is None or title is null.')

		res = {'node':node, 'selector':selector(node), 'text':''}
		text = node.text_content()
		if text and text in title:
			res['text'] = text
			return res

		maxlen = 0
		for child in node.iter():
			if child.text and child.text.strip():
				text = child.text.strip()
				if len(text) >= maxlen and (title.startswith(text) or title.endswith(text)):
					maxlen, res['text'] = len(text), text
			if child.tail and child.tail.strip():
				text = child.tail.strip()
				if len(text) >= maxlen and (title.startswith(text) or title.endswith(text)):
					maxlen, res['text'] = len(text), text
		return res