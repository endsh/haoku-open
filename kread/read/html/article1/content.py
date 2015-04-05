# coding: utf-8
from .base import BaseParser, ArticleNotFound


class ContentParser(BaseParser):

	def parse(self):
		res = {'text':'', 'selector':'', 'score':0, 'node':None}
		return res