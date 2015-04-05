# coding: utf-8
from utils import load_data, save_data, remove_data


class LocalFile(object):
	""" mongodb file class """

	def __init__(self, conf):
		""" init class """
		self.conf = conf
		self.path = conf['path']

	def get_link(self, name):
		return self.conf['link'] % name

	def get(self, name):
		""" get file content """
		return load_data(self.path + '/' + name)

	def put(self, name, content, type=None):
		if type is not None:
			name = '%s.%s' % (name, type)
		else:
			name = name
		path = '%s/%s' % ('/'.join(name[:3]), name)
		save_data(self.path + '/' + path, content)
		return path

	def remove(self, name):
		remove_data(name)
