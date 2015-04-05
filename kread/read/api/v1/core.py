# coding: utf-8
import conf
import random
from flask import current_app
from simin.web.core import api, cache
from accounts.sdk.access import AccessManager
from accounts.client.v1 import BaseAccounts, Accounts
from db import MongoIWeb
from index.simin import TAGS

access = AccessManager()
access.setup_user(
	publics=dict(
		accounts=BaseAccounts,
	),
	privates=dict(
		accounts=Accounts,
	),
)

mongo = MongoIWeb(conf.mongo_iweb)

cates = u'科技数码|互联网|明星娱乐|体育资讯|军事观察|汽车资讯|' \
		u'财经热点|教育新闻|星座命理|科学探索|两性话题'.split('|')
topics = {}
hots = []
for topic, words in TAGS.iteritems():
	words = words.split('|')
	topics[topic] = words
	hots.extend(words)

hots = list(set(hots))


def img2url(path, width=0, height=0, ystart=0, yend=0):
	if current_app.status == 'DEBUG':
		return 'http://0.0.0.0:3003/img/%s' % path

	if width == 0 or height == 0:
		return 'http://img.haoku.net/%s@95Q.jpg' % path

	if ystart == 0 and yend == 0:
		return 'http://img.haoku.net/%s@%dw_%dh_1e_1c_95Q.jpg' % (path, width, height)

	return 'http://img.haoku.net/%s@0-%d-0-%da_%dw_%dh_1e_1c_95Q.jpg' \
		% (path, ystart, yend, width, height)


def icon2url(icon, width=150, height=120):
	if icon['width'] * 0.8 < icon['height']:
		ystart = int(icon['height'] * 0.05)
		yend = int(ystart + height * icon['width'] / width) 
		return img2url(icon['path'], width, height, ystart, yend)
	return img2url(icon['path'], width, height)


@cache.memoize(timeout=300)
def find_article(id):
	return mongo.article.find_one(id)



def find_articles(key, ids, fields=None):
	articles = []
	cache_key = cache._memoize_make_cache_key()
	keys = dict((id, cache_key(find_articles, key, id, fields)) for id in ids)
	waits = []
	for id in ids:
		art = cache.get(keys[id])
		if art is None:
			waits.append(id)
		else:
			articles.append(art)

	if fields and key not in fields:
		fields[key] = 1

	arts = list(mongo.article.find({key:{'$in':waits}}, fields=fields))
	for art in arts:
		cache.set(keys[art[key]], art, 1800)
	articles.extend(arts)
	return articles


@cache.memoize(timeout=120)
def find_topic(word, last=None, limit=20):
	if word in cates:
		return mongo.topic.find(word, last=last, limit=limit)
	return mongo.index.find(word, last=last, limit=limit)


@cache.memoize(timeout=120)
def find_topic_page(word, page):
	if word in cates:
		return mongo.topic.find_page(word, page)
	return mongo.index.find_page(word, page)


def remove_index(doc):
	mongo.topic.remove(doc)
	mongo.index.remove(doc)


def tags2icon(tags):
	res = {}
	waits = {}
	for tag in tags:
		lower = tag.lower()
		icon = cache.get(u't-%s' % lower)
		if icon is not None:
			res[tag] = icon
		else:
			waits[tag] = lower
	if waits:
		icons = mongo.index.find_tags(waits.values(), {'icon':1})
		icons = dict((x['_id'], x['icon']) for x in icons)
		for tag, lower in waits.iteritems():
			if lower in icons:
				res[tag] = icons[lower]
			else:
				res[tag] = ''
			cache.set(u't-%s' % lower, res[tag], timeout=1800)

	for tag, icon in res.iteritems():
		if icon:
			res[tag] = img2url(icon, width=150, height=120)
		else:
			res[tag] = img2url('default.jpg', width=150, height=120)
	return res


@cache.memoize(timeout=1800)
def tag2icon(tag):
	index = mongo.index.find_index(tag, {'icon':1})
	if index and index['icon']:
		return img2url(index['icon'], width=150, height=120)
	return ''


@cache.memoize(timeout=900)
def get_hots(key):
	tags = []
	while True:
		tag = random.choice(hots)
		if tag in tags:
			continue
		tags.append(tag)
		if len(tags) == 9:
			break
	return tags2icon(tags)


@cache.memoize(timeout=300)
def get_keywords(key):
	keywords = u'IS公布首脑录音|乌克兰危机|G20会议焦点|俄空军飞行表演|习近平举行宴会|保时捷|上海通用汽车' \
		u'|女子约会他人|新车抢先看|黄金白银|金价围绕低点反弹|美国中期选举|原来有你|词组搜索还在开发中'.split('|')
	return keywords


def init_core(app):
	access.init_app(app)
	api.init_app(app)
	cache.init_app(app)
