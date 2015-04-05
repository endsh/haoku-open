# coding: utf-8
from .base import MongoBase
from .index import MongoIndex, MongoReIndex
from .topic import MongoTopic, MongoReTopic
from .comment import MongoComment
from .feedback import MongoFeedback
from .ossfile import OssFile
from .local import LocalFile

__all__ = [
	'MongoWeb',
]


class MongoWeb(MongoBase):

	def __init__(self, conf):
		super(MongoWeb, self).__init__(conf)
		self.db = self.conn.read
		self.article = self.db.article
		self.image = self.db.image
		self.index = MongoIndex(self.conn.index)
		self.topic = MongoTopic(self.conn.topic)
		self.comment = MongoComment(self.conn.comment)
		self.feedback = MongoFeedback(self.conn.feedback)
		if conf['storage'] == 'oss':
			self.image_file = OssFile(conf['image_file'])
			self.text_file = OssFile(conf['text_file'])
		else:
			self.image_file = LocalFile(conf['image_file'])
			self.text_file = LocalFile(conf['text_file'])
