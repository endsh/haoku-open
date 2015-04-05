# coding: utf-8
import re

CATES = u'新闻|科技|数码|娱乐|体育|军事|教育|财经|旅游|文化|历史|健康|美食|时尚|星座|女性|育儿|汽车|房产|家居|公益|佛学|摄影|图片|城市'.split('|')
REGEXES = {
	'time': re.compile(u'(((19|20)\d{2})([-\./]|年)([01]?\d)([-\./]|月)([0-3]?\d)日?)[ ,]*(([0-2]?\d):([0-6]\d)(:([0-6]\d))?)?'),
	'positive': re.compile('article|body|content|entry|hentry|main|page|pagination|post|text|blog|story', re.I),
	'negative': re.compile('combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget', re.I),
}


class ArticleNotFound(Exception):
	pass


class BaseParser(object):

	def __init__(self, article):
		self.article = article
		self.options = article.options

	def parse(self):
		raise NotImplementedError