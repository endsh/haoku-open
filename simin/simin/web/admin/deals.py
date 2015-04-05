# coding: utf-8
from pymongo.collection import Collection
from flask.ext.admin import tools
from flask.ext.admin.base import expose


def _url_formatter(*args, **kwargs):
	url = args[0]
	return url

def deal(title, url, style='info', ajax=True):

	def wrap(f):
		f._deal = (title, url, style, ajax)
		expose(_url_formatter(url))(f)
		return f

	return wrap


class DealsMixin(object):
	
	def __init__(self):
		self._deals = []

	def add(self, deals):
		pass

	def init_deals(self):
		if not hasattr(self, '_deals'):
			self._deals = []

		for p in dir(self):
			attr = tools.get_dict_attr(self, p)
			if not isinstance(attr, Collection) \
					and hasattr(attr, '_deal'):
				title, url, style, ajax = attr._deal
				self._deals.append({
					'title':title,
					'url':'.' + attr.__name__,
					'style':style,
					'ajax':ajax,
				})

	def get_deals(self):
		return self._deals