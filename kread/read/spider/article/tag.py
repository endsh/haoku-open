# coding: utf-8
import json
import math
import time
import hashlib
from collections import OrderedDict
from datetime import datetime
from spider.cmd import handle
from .base import ArtBase


class Art2MakeTag(ArtBase):

	def __init__(self, articles):
		super(Art2MakeTag, self).__init__(
			articles=articles,
			cmd='tag',
		)

	def handle(self, key, res):
		if key not in self.doing:
			self.log.warn('article is not found in keyword: %s' % key)
			return

		article = self.doing.pop(key)
		article['last'] = time.time()
		if 'exc' not in res:
			article['tags'] = res['tags']
			if len(article['tags']) >= 3 and article['icons']:
				self.master.topics.add(article)
			self.finish(article)
			self.log.debug('tags: %s\n====> %s' % (article['url'], '  +  '.join(res['tags'])))
		else:
			article['exc'] = res['exc']
			self.error(article)
			self.log.warn('keyword exception (%s) from %s.'
				% (res['exc'], article['url']))


def make_tags(handler, article, keys, words):
	def score(word, num):
		word = word.lower()
		md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
		df = handler.redis_tag.hget(md, word)
		df = max(int(df), 0) if df is not None else 0
		if df < 10:
			return 0
		return num * max(math.log(df + 1, 50), 1.5)

	dfs = words['dfs'].copy()
	dfs.update(words['efs'])
	dfs = [(x, score(x, y)) for x, y in sorted(dfs.iteritems(), key=lambda x: -x[1])[:20]]
	dfs = filter(lambda x: x[1] > 0, dfs)

	tags = OrderedDict(sorted(dfs, key=lambda x: -x[1])).keys()

	for tag in list(tags):
		sub = False
		for other in tags:
			if tag == other:
				sub = True
			elif tag in other:
				if len(tag) < 4 and len(other) >= 4 or sub == False:
					if tag in tags:
						tags.remove(tag)
				else:
					tags.remove(other)
	return tags[:6]


def update_index(handler, article, keys, words):
	redis_tag = handler.redis_tag
	mongo = handler.mongo_spider
	mongo_web = handler.mongo_web

	if article['v']['tag'] > 0 and article['sim'] == True:
		row = mongo.keyword.find_one({'_id':article['_id']}, {'sim':1, 'keys':1, 'words':1})
		if row is not None and row['sim'] == True:
			row['words'] = json.loads(row['words'])
			for word in row['keys']:
				md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
				redis_tag.hincrby(md, word, -1)
			redis_tag.incr('total', -1)

			for word in row['words']['index']:
				mongo_web.index.remove(word, article['_id'])

			if article['sim'] != True:
				mongo_web.article.remove(article['_id'])

	mongo.keyword.save({
		'_id': article['_id'],
		'sim': article['sim'],
		'keys': keys,
		'words': json.dumps(words),
	})

	tags = []
	if article['sim'] == True:
		for word in keys:
			md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
			redis_tag.hincrby(md, word, 1)
		redis_tag.incr('total', 1)

		tags = make_tags(handler, article, keys, words)
		article['tags'] = tags
		article['last'] = time.time()
		mongo_web.article.save(article)

		imgs = len(article['imgs'])

		icons = article['icons'].values()
		ilen, tlen, alen, blen = len(icons), len(tags), 0, 0

		xtags = set(list(tags))
		for word, num in words['index'].iteritems():
			if word in xtags:
				xicons = icons
			else:
				xicons = []
			mongo_web.index.add(word, article['_id'], num, imgs, article['pubtime'], xicons)

		#handler.cluster_redis.zadd('waiting', article['_id'], -article['pubtime'])

	return tags


class KeywordError(ValueError):
	pass


@handle('tag')
def keyword(handler, key, article, ext):
	row = handler.mongo_spider.word.find_one({'_id':article['_id']}, {'sim':1, 'words':1})
	if row is None:
		raise KeywordError('Words not found.')
	words = json.loads(row['words'])
	res = handler.keyword.make(article['title'], words)
	if res is None:
		raise KeywordError('Keyword not found.')
	tags = update_index(handler, article, res['keys'], res['words'])
	return {'tags':tags}
