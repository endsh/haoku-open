# coding: utf-8
from utils import html2doc
from .base import BaseParser

__all__ = [
	'ImgsParser',
]


class ImgsParser(BaseParser):

	def parse(self):
		imgs = set()
		doc = html2doc(self.article.content)
		for img in doc.iter('img'):
			src = img.get('src')
			if src and src.strip():
				imgs.add(src.strip())
		return {'urls':list(imgs)}