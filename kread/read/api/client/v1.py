# coding: utf-8
from accounts.sdk.client import Client
from .settings import API_V1_HOST


class BaseReader(Client):

	def __init__(self, user):
		super(BaseReader, self).__init__(user, API_V1_HOST)

	def index(self):
		return self.get('/index')

	def latest(self):
		return self.get('/latest')

	def cates(self):
		return self.get('/cates')

	def article(self, id):
		return self.get('/articles/%s/' % id)

	def comments(self, id, page=None):
		args = dict(page=page) if page is not None else {}
		return self.get('/articles/%s/comments' % id, args=args)

	def latest(self, last=None, limit=None, hots=False):
		args = dict(last=last) if last is not None else {}
		if limit is not None:
			args['limit'] = limit
		if hots == True:
			args['hots'] = 'true'
		return self.get('/latest', args=args)

	def topic(self, word, last=None, limit=None, hots=False):
		args = dict(last=last) if last is not None else {}
		if limit is not None:
			args['limit'] = limit
		if hots == True:
			args['hots'] = 'true'
		return self.get('/topics/%s/' % word, args=args)

	def topic_page(self, word, page=1):
		return self.get('/topics/%s/%d' % (word, page))


class Reader(BaseReader):
	
	def post_comment(self, id, content):
		return self.post('/articles/%s/post-comment' % id, dict(content=content))