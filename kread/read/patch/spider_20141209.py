# coding: utf-8
from gevent import monkey; monkey.patch_socket()
import socket
socket.setdefaulttimeout(300)
import conf
import gevent.pool
import json
import redis
import sys
import hashlib
import math
import urllib
import pymongo.errors
from collections import OrderedDict
from index import Keyword
from utils import unicode2hash, hash2long, html2doc, child2html
from .base import spider, find2do, iweb
from .cmd import *

redis_word = redis.Redis(**conf.redis_word)
redis_tag = redis.Redis(**conf.redis_tag)
redis_time = redis.Redis(**conf.redis_time)
redis_url = redis.Redis(**conf.redis_url)
keyword = Keyword(redis_word)
pool = gevent.pool.Pool(100)

keys = '_id|domain|tpl|title|src_link|created|html|src_type|src|src_name|last|url|pubtime|f|v|version|imgs|pages'.split('|')


# coding: utf-8
import time
import json
import random
from collections import defaultdict
from index.simin import SIMIN


def init_simin():
	res = {}
	for topic, words in SIMIN.iteritems():
		res[topic] = words.lower().split('|')
	return res


class Topics(object):

	def __init__(self):
		self.topic = iweb.topic
		self.simin = init_simin()

	def add(self, article):
		res = defaultdict(int)
		for topic, words in self.simin.iteritems():
			for tag in article['tags']:
				if tag in words:
					res[topic] += 1
		if not res:
			return

		topic, cnt = max(res.iteritems(), key=lambda x: x[1])
		if cnt < 2:
			return

		xicons = [x['path'] for x in article['icons'].values()]
		while True:
			try:
				self.topic.add(topic, article['long'], len(article['icons']), article['pubtime'], xicons)
				break
			except (pymongo.errors.OperationFailure, IndexError), e:
				print str(e)
				gevent.sleep(1)
		return topic


topics = Topics()


def time2id(pubtime):
	date = time.strftime('%Y%m%d', time.localtime(pubtime))
	index = int(redis_time.hincrby(date[:4], date, 1)) + 10000
	return date, '%s%d' % (date, index)


def replace2tag(doc, index, start=0):
	if doc.text and doc.tag != 'a':
		text = doc.text
		stext = doc.text[max(4-start, 0):]
		for word in index:
			if word in stext:
				index.remove(word)
				x = text.index(word)
				doc.text = text[:x]
				link = '/topics/%s.html' % word
				sub = doc.makeelement('a', {'href':link, 'class':'tag'})
				sub.text = word
				doc.insert(0, sub)
				sub.tail = text[x+len(word):]
				start = 0
				break
		else:
			start += len(doc.text)

	for child in doc.getchildren():
		start = replace2tag(child, index, start)

	if doc.tail:
		text = doc.tail
		stext = doc.tail[max(4-start, 0):]
		for word in index:
			if word in stext:
				index.remove(word)
				x = text.index(word)
				link = '/topics/%s.html' % word
				sub = doc.makeelement('a', {'href':link, 'class':'tag'})
				sub.text = word
				doc.addnext(sub)
				doc.tail = text[:x]
				sub.tail = text[x+len(word):]
				start = 0
				break
		else:
			start += len(doc.tail)
	return start

def web_content(row, article, words):
	def score(word, num):
		word = word.lower()
		md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
		df = redis_tag.hget(md, word)
		df = max(int(df), 0) if df is not None else 0
		if df < 10:
			return 0
		return num * max(math.log(df + 1, 50), 1.5)

	index = [(x, score(x, y)) for x, y in sorted(words['words']['all'].iteritems(), key=lambda x: -x[1])]
	index = dict(filter(lambda x: x[1] > 0 and x[0] not in article['tags'], index)).keys()

	index = index[:int(len(words['words']['all']) * 0.25)]

	if index:
		doc = html2doc(row['content'])
		replace2tag(doc, index)
		content = child2html(doc)
		return content
	return row['content']


from simhash import Simhash
from utils import html2text


def sim(article, content):
	while True:
		try:
			# if 'sim' in article and article['sim'] != False:
			# 	iweb.sim.unset(article['long'], article['sim'])
			content = html2text(content)
			if len(content) < 20:
				text = article['title'] + content
			else:
				text = content

			num = Simhash(text).value - sys.maxint
			near = iweb.sim.near(num)

			key = iweb.sim.save(article['long'], num, near)
			return key
		except (pymongo.errors.OperationFailure, IndexError), e:
			print str(e)
			gevent.sleep(1)


def make_tags(article, index):
	def score(word, num):
		word = word.lower()
		md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
		df = redis_tag.hget(md, word)
		df = max(int(df), 0) if df is not None else 0
		if df < 10:
			return 0
		return num * max(math.log(df + 1, 50), 1.5)

	index = [(x, score(x, y)) for x, y in sorted(index.iteritems(), key=lambda x: -x[1])]
	index = filter(lambda x: x[1] > 0, index)

	tags = OrderedDict(sorted(index, key=lambda x: -x[1])).keys()

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


def update_index(article, words):
	res = keyword.make(article['title'], words['words'])
	if res is None:
		words['keys'] = []
		words['index'] = {}
		return words, []

	words['keys'] = res['keys']
	words['index'] = res['index']

	tags = []
	if article['sim'] == True:
		for word in words['keys']:
			md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
			redis_tag.hincrby(md, word, 1)
		redis_tag.incr('total', 1)

		tags = make_tags(article, words['index'])

		imgs = len(article['imgs'])
		icons = [x['path'] for x in article['icons'].values()]
		ilen, tlen, alen, blen = len(icons), len(tags), 0, 0

		xtags = set(list(tags))
		for word, num in words['index'].iteritems():
			if word in xtags:
				xicons = icons
			else:
				xicons = []
			while True:
				try:
					iweb.index.add(word, article['long'], num, imgs, article['pubtime'], xicons)
					break
				except (pymongo.errors.OperationFailure, IndexError), e:
					print str(e)
					gevent.sleep(1)

	return words, tags


def _upgrade_article(row):
	article = dict((x, row[x]) for x in keys)

	xlong = unicode2hash(article['url'])
	redis_url.sadd(article['domain'], xlong)
	article['long'] = xlong
	article['pubdate'], article['id'] = '', ''

	del article['v']['tag']

	article['icons'] = row['icons']

	if 'content' in row and row['content']:
		article['content'] = iweb.text_file.put('spider_%s' % article['_id'], row['content'].encode('utf-8'), 'txt')
	else:
		article['content'] = ''
	
	if article['v']['sim'] > 0:
		article['sim'] = sim(article, row['content'])
	else:
		article['sim'] = False

	if row['v']['seg'] > 0:
		# article['pubdate'], article['id'] = time2id(article['pubtime'])
		# article['words'] = article['_id']
		# words = iweb.word_file.get(article['words'])
		# if words is not None:
		# 	words = json.loads(words)
		# 	words['sim'] = article['sim']
		# 	words, article['tags'] = update_index(article, words)
		# 	iweb.word_file.put(row['_id'], json.dumps(words))

		# 	web_article = {
		# 		'_id': article['_id'],
		# 		'id': article['id'],
		# 		'long': article['long'],
		# 		'title': article['title'],
		# 		'domain': article['domain'],
		# 		'src_name': article['src_name'],
		# 		'src_link': article['src_link'],
		# 		'tags': article['tags'],
		# 		'icons': article['icons'],
		# 		'url': article['url'],
		# 		'sim': article['sim'],
		# 		'icons': article['icons'],
		# 		'pubtime': article['pubtime'],
		# 		'last': article['last'],
		# 	}
		# 	content = web_content(row, article, words)
		# 	web_article['content'] = iweb.text_file.put('web_%s' % article['_id'], content.encode('utf-8'), 'txt')
		# 	while True:
		# 		try:
		# 			iweb.article.save(web_article)
		# 			break
		# 		except pymongo.errors.OperationFailure, e:
		# 			print str(e)
		# 			gevent.sleep(1)

		# 	if len(article['tags']) >= 3 and article['icons']:
		# 		topics.add(web_article)
		# else:
		# 	row['exc'] = 'ValueError'
		pass
	else:
		article['words'] = ''
		article['tag'] = []

	if row['exc']:
		article['exc'] = row['exc']

		while True:
			try:
				iweb.spider_exc.save(article)
				break
			except pymongo.errors.OperationFailure, e:
				print str(e)
				gevent.sleep(1)
	else:
		while True:
			try:
				iweb.spider_article.save(article)
				break
			except pymongo.errors.OperationFailure, e:
				print str(e)
				gevent.sleep(1)


count = 0
def upgrade_article(row):
	pool.spawn(_upgrade_article, row)

	global count
	count += 1
	if count > 50:
		count = 0
		for greenlet in list(pool):
			if greenlet.dead:
				pool.discard(greenlet)


@remote()
def upgrade(skip=None, limit=None):
	if skip is not None:
		skip = int(skip) * 100000
	if limit is not None:
		limit = int(limit) * 100000
	find2do(spider.article, {}, upgrade_article, skip=skip, limit=limit)


if __name__ == '__main__':
	main()
