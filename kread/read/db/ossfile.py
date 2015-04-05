# coding: utf-8
from oss.oss_api import OssAPI

__all__ = [
	'OssFile',
]


class OssFile(object):

	def __init__(self, conf):
		self.conf = conf
		self.oss = OssAPI(
			conf['host'],
			conf['access_id'],
			conf['secret_access_key'],
		)

	def get_link(self, path):
		return self.conf['link'] % path

	def get(self, name):
		res = self.oss.get_object(self.conf['bucket'], name)
		if (res.status / 100) == 2:
			return res.read()
		return ''

	def put(self, name, content, type=None):
		if type is not None:
			path = '%s.%s' % (name, type)
		else:
			path = name
			
		res = self.oss.put_object_from_string(self.conf['bucket'], path, content)
		if (res.status / 100) == 2:
			return path
		return ''

	def remove(self, name):
		res = self.oss.delete_object(self.conf['bucket'], name)
		if (res.status / 100) == 2:
			return True
		return False
