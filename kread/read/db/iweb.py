# coding: utf-8
from .base import MongoBase
from .index import MongoIndex, MongoReIndex
from .topic import MongoTopic, MongoReTopic
from .comment import MongoComment
from .feedback import MongoFeedback
from .ossfile import OssFile
from .local import LocalFile
from .sim import MongoSim

__all__ = [
	'MongoIWeb',
]


class MongoIWeb(MongoBase):

	def __init__(self, conf):
		super(MongoIWeb, self).__init__(conf)
		self.db = self.conn.read
		self.article = self.db.article
		self.index = MongoReIndex(self.conn.index)
		self.topic = MongoReTopic(self.conn.index)
		self.comment = MongoComment(self.conn.comment)

		self.spider = self.conn.spider
		self.spider_article = self.spider.article
		self.spider_exc = self.spider.exc_article
		self.domain = self.spider.domain
		self.catecory = self.spider.catecory
		self.template = self.spider.template
		self.image = self.spider.image
		self.sim = MongoSim(self.conn.sim)

		if conf['storage'] == 'oss':
			self.image_file = OssFile(conf['image_file'])
			self.html_file = OssFile(conf['html_file'])
			self.word_file = OssFile(conf['word_file'])
			self.text_file = OssFile(conf['text_file'])
		else:
			self.image_file = LocalFile(conf['image_file'])
			self.html_file = LocalFile(conf['html_file'])
			self.word_file = LocalFile(conf['word_file'])
			self.text_file = LocalFile(conf['text_file'])
