# coding: utf-8
from .base import MongoBase
from .index import MongoIndex
from .topic import MongoTopic
from .comment import MongoComment
from .feedback import MongoFeedback
from .ossfile import OssFile
from .local import LocalFile

__all__ = [
	'MongoAdmin',
]


class MongoAdmin(MongoBase):

	def __init__(self, conf):
		super(MongoAdmin, self).__init__(conf)
		self.db = self.conn.xadmin
		self.role = self.db.role
		self.user = self.db.user
		self.task = self.db.task
		self.recode = self.db.recode
		self.simhash = self.db.simhash
