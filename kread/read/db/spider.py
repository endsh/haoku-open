# coding: utf-8
from .base import MongoBase
from .ossfile import OssFile
from .local import LocalFile
from .sim import MongoSim


class MongoSpider(MongoBase):

	def __init__(self, conf):
		super(MongoSpider, self).__init__(conf)
		self.db = self.conn.read
		self.domain = self.db.domain
		self.catecory = self.db.catecory
		self.template = self.db.template
		self.article = self.db.article
		self.image = self.db.image
		self.word = self.db.word
		self.keyword = self.db.keyword
		self.log = self.db.log
		self.sim = MongoSim(self.conn.sim)

		if conf['storage'] == 'oss':
			self.html_file = OssFile(conf['html_file'])
			self.word_file = OssFile(conf['word_file'])
			self.text_file = OssFile(conf['text_file'])
		else:
			self.html_file = LocalFile(conf['html_file'])
			self.word_file = LocalFile(conf['word_file'])
			self.text_file = LocalFile(conf['text_file'])
