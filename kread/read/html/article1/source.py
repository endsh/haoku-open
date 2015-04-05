# coding: utf-8
import re
from utils import get_domain
from .base import BaseParser, CATES, REGEXES
from ..doc import selector

__all__ = [
	'SourceParser',
]


class SourceParser(BaseParser):

	def parse(self):
		node = self.get_source_node()
		return self.node2source(node)

	def get_source_node(self):
		if self.options.get('source_selector', ''):
			nodes = self.article.select(self.options['source_selector'])
			if len(nodes) == 1:
				return nodes[0]
			for node in nodes:
				res = self.has_source(node)
				if res is not None:
					return res

		for node in self.article.doc.find('body').iter():
			res = self.has_source(node)
			if res is not None:
				return res

		domain = get_domain(self.article.url)
		for a in self.article.doc.iter('a'):
			link = a.get('href')
			if link and link.startswith('http') \
					and get_domain(link) != domain:
				text = self.article.get_block_text(a)
				if len(text) >= 2:
					if text.endswith(u'报') and not text.endswith(u'举报') \
							or text[-2:] in CATES and len(text) == 4:
						return a

	def has_source(self, node):
		if node.text and node.text.strip():
			text = node.text.strip()
			if text and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
				return node
		if node.tail and node.tail.strip():
			text = node.tail.strip()
			if text and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
				return node

	def node2source(self, node):
		res = {'text':'', 'link':'', 'selector':'', 'node':node}
		if node is None:
			return res

		res['selector'] = selector(node)
		link = ''
		text = node.text.strip() if node.text else ''
		tail = node.tail.strip() if node.tail else ''
		if text and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
			text = text[text.index(u'源') + 2:].strip()
			if not text:
				for child in node.iter():
					if child == node:
						continue
					if child.text and child.text.strip():
						text = child.text.strip()
						if child.tag == 'a':
							link = child.get('href', '')
						break
					if child.tail and child.tail.strip():
						text = child.tail.strip()
						break
				if not text:
					text = tail
					if not text:
						link, text = self.article.get_next_text(node)
			text = text.split('|')[0] if text else ''
			text = text.split()[0] if text else ''
		elif tail and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
			text = text[tail.index(u'源') + 2:].strip()
			if not text:
				link, text = self.article.get_next_text(node)
			text = text.split('|')[0] if text else ''
			text = text.split()[0] if text else ''
		else:
			link, text = node.get('href', ''), self.article.get_block_text(node)

		if (len(text) <= 8 or len(text) < 20 and re.match('^[\w ]+$', text)) \
				and not REGEXES['time'].search(text):
			res['link'], res['text'] = link, text
		return res