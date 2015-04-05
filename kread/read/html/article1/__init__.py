# coding: utf-8
from utils import clean_html, doc2html
from .title import *
from .source import *
from .content import *
from .pubtime import *
from .pages import *
from .imgs import *

__all__ = [
	'Article', 'html2article',
]
BLOCK_TAGS = ['div','p','table','td','article','section','pre']
BLOCK_XPATH = '|'.join(['.//%s' % x for x in BLOCK_TAGS])

class Article(object):

	def __init__(self, input, url, **options):
		self.input = input
		self.url = url
		self.options = options

		self.doc = clean_html(input, url, return_doc=True)
		self.html = doc2html(self.doc)

	def get_block_text(self, node, default=''):
		if node.xpath(BLOCK_XPATH):
			return default
		text = ''
		for child in node.iter():
			if child.text:
				text += child.text.strip()
			if child != node and child.tail:
				text += child.tail.strip()
		return text

	def get_next_text(self, node, default_text='', default_link=''):
		link = ''
		for sib in node.itersiblings():
			for child in sib.iter():
				if child.text and child.text.strip():
					if child.tag == 'a':
						link = child.get('href', '')
					return link, child.text.strip()
				if child.tail and child.tail.strip():
					return link, child.tail.strip()
		return default_link, default_text

	def select(self, selector):
		return self.doc.cssselect(selector)

	@property
	def selector(self):
		return {
			'title': self.xtitle['selector'],
			'source': self.xsource['selector'],
			'content': self.xcontent['selector'],
		}

	@property
	def article(self):
		return {
			'title': self.title,
			'link': self.link,
			'source': self.source,
			'content': self.content,
			'pubtime': self.pubtime,
			'pages': self.pages,
			'imgs': self.imgs,
		}


def add_parser(cls, name, parser, default='text', ext=None):

	def wrapper(key, value):
		def obj(self):
			if not hasattr(self, '_%s' % value):
				setattr(self, '_%s' % value, getattr(self, 'x%s' % name)[key])
			return getattr(self, '_%s' % value)
		return obj

	def xobj(self):
		if not hasattr(self, '_x%s' % name):
			p = parser(self)
			setattr(self, '_x%s' % name, p.parse())
		return getattr(self, '_x%s' % name)

	if isinstance(default, str):
		setattr(cls, name, property(wrapper(default, name)))
	if isinstance(ext, str):
		setattr(cls, ext, property(wrapper(ext, ext)))
	
	setattr(cls, 'x%s' % name, property(xobj))

add_parser(Article, 'title', TitleParser)
add_parser(Article, 'source', SourceParser, ext='link')
add_parser(Article, 'content', ContentParser)
add_parser(Article, 'pubtime', TimeParser, default='int')
add_parser(Article, 'pages', PagesParser, default='urls')
add_parser(Article, 'imgs', ImgsParser, default='urls')


def html2article():
	pass