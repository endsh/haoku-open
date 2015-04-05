# coding: utf-8
import json
import time
import math
import hashlib
import pymongo.errors
from collections import OrderedDict
from index import segmentor
from utils import html2text, html2doc, child2html, unicode2hash
from spider.cmd import handle
from .base import ArtBase


class Art2Segment(ArtBase):

	def __init__(self, articles):
		super(Art2Segment, self).__init__(
			articles=articles,
			cmd='seg',
			ext_list=['content'],
		)
		self.redis = self.articles.redis_word

	def handle(self, key, res):
		if key not in self.doing:
			self.log.warn('article is not found in segment: %s' % key)
			return

		article = self.doing.pop(key)
		article['last'] = time.time()
		if 'exc' not in res:
			article['pubdate'] = res['pubdate']
			article['id'] = res['id']
			article['words'] = res['words']
			article['tags'] = res['tags']
			if len(article['tags']) >= 3 and article['icons']:
				self.master.topics.add(article)
			self.finish(article)
		else:
			article['exc'] = res['exc']
			self.error(article)
			self.log.warn('segment exception (%s) from %s.'
				% (res['exc'], article['url']))


def time2id(handler, pubtime):
	date = time.strftime('%Y%m%d', time.localtime(pubtime))
	index = int(handler.redis_time.hincrby(date[:4], date, 1)) + 10000
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

def web_content(handler, article, words, ext):
	def score(word, num):
		word = word.lower()
		md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
		df = handler.redis_tag.hget(md, word)
		df = max(int(df), 0) if df is not None else 0
		if df < 10:
			return 0
		return num * max(math.log(df + 1, 50), 1.5)

	index = [(x, score(x, y)) for x, y in sorted(words['words']['all'].iteritems(), key=lambda x: -x[1])]
	index = dict(filter(lambda x: x[1] > 0 and x[0] not in article['tags'], index)).keys()

	index = index[:int(len(words['words']['all']) * 0.25)]

	if index:
		doc = html2doc(ext['content'])
		replace2tag(doc, index)
		content = child2html(doc)
		return content
	return ext['content']


def make_tags(handler, article, index):
	def score(word, num):
		word = word.lower()
		md = hashlib.md5(word.encode('utf-8')).hexdigest()[:2]
		df = handler.redis_tag.hget(md, word)
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


def update_index(handler, article, words):
	res = handler.keyword.make(article['title'], words['words'])
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
			handler.redis_tag.hincrby(md, word, 1)
		handler.redis_tag.incr('total', 1)

		tags = make_tags(handler, article, words['index'])

		imgs = len(article['imgs'])
		icons = [x['path'] for x in article['icons'].values()]
		ilen, tlen, alen, blen = len(icons), len(tags), 0, 0

		xtags = set(list(tags))
		for word, num in words['index'].iteritems():
			if word in xtags:
				xicons = icons
			else:
				xicons = []
			handler.mongo.index.add(word, article['long'], num, imgs, article['pubtime'], xicons)

	return words, tags


def save_words(handler, article, words, ext):
	redis_word = handler.redis_word
	mongo = handler.mongo

	if 'word' in article and article['word']:
		row = mongo.word_file.get({article['word']})
		if row:
			row = json.loads(row)
			if row['sim'] == True:
				row['words'] = json.loads(row['words'])
				for word, cnt in row['words']['all'].iteritems():
					word = word.lower()
					hkey = unicode2hash(word)
					key = hkey % 500
					redis_word.hincrby(key, hkey, -1)
				redis_word.incr('total', -1)

	if article['sim'] == True:
		for word, cnt in words['all'].iteritems():
			word = word.lower()
			hkey = unicode2hash(word)
			key = hkey % 500
			redis_word.hincrby(key, hkey, 1)
		redis_word.incr('total', 1)

	if 'id' not in article or not article['id']:
		article['pubdate'], article['id'] = time2id(handler, article['pubtime'])
	else:
		article['pubdate'] = time.strftime('%Y%m%d', time.localtime(pubtime))
	article['words'] = article['_id']

	words = {'words':words, 'sim':article['sim']}
	
	words, article['tags'] = update_index(handler, article, words)
	mongo.word_file.put(article['_id'], json.dumps(words))

	web_article = {
		'_id': article['_id'],
		'id': article['id'],
		'long': article['long'],
		'title': article['title'],
		'domain': article['domain'],
		'src_name': article['src_name'],
		'src_link': article['src_link'],
		'tags': article['tags'],
		'icons': article['icons'],
		'url': article['url'],
		'sim': article['sim'],
		'icons': article['icons'],
		'pubtime': article['pubtime'],
		'last': article['last'],
	}
	content = web_content(handler, article, words, ext)
	web_article['content'] = mongo.text_file.put('web_%s' % article['_id'], content.encode('utf-8'), 'txt')
	while True:
		try:
			mongo.article.save(web_article)
			break
		except pymongo.errors.OperationFailure, e:
			time.sleep(1)


@handle('seg')
def segment(handler, key, article, ext):
	if 'content' not in ext or not ext['content']:
		ext['content'] = handler.text_file.get(article['content'])
		if not ext['content']:
			raise ValueError('load content failed.')
		ext['content'] = content.decode('utf-8')

	words = segmentor.seg(article['title'], html2text(ext['content']))
	save_words(handler, article, words, ext)

	return {
		'pubdate': article['pubdate'],
		'id': article['id'],
		'words': article['words'],
		'tags': article['tags'],
	}
