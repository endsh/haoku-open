# coding: utf-8
import requests
import conf
import gevent
import json
import os
import urlparse
from gevent import Timeout
from gevent.monkey import patch_socket
from db import MongoSpider, MongoWeb
from utils import queue, auto_work, logger, get, atime, cmd
from utils.worker import GeventWorker, KGreenletExit, Worker
from deal.html import HtmlDiff, Document
from spider.rss import RssParser
from lxml import html
import logging
import difflib2
import urlparse
import datetime


@cmd('select-rss')
def select_rss():
	mongo = MongoSpider(conf.mongo_spider)
	with open(conf.data_root + os.sep + 'filter.json') as fd:
		data = fd.read()
	feeds = json.loads(data)
	good = dict(filter(lambda x: x[1]['status'] == 'good' and x[1]['language'] =='zh', feeds.iteritems()))
	feeds = {}
	keys = "_id,url,link,title,description,image,copyright,ttl,has_content".split(',')
	for id, feed in good.iteritems():
		new = {}
		for key in keys:
			if key in feed:
				new[key] = feed[key]
			else:
				new[key] = ''
		new['lang'] = feed['language']
		new['name'] = ''
		for key in 'score,count,next,null,last_time,add_time'.split(','):
			new[key] = 0
		new['last_link'] = ''
		feeds[id] = new
	with open(conf.data_root + os.sep + 'good.json', 'w+') as fd:
		fd.write(json.dumps(feeds))


@cmd('oss-test')
def oss_test():
	mongo = MongoSpider(conf.mongo_spider)
	mongo.oss.put('oss-test', 'hello, oss!' + str(datetime.datetime.now()))
	print mongo.oss.get('oss-test')


@cmd('del-rss')
def del_rss():
	mongo = MongoSpider(conf.mongo_spider)
	with open(conf.data_root + os.sep + 'good.json') as fd:
		data = fd.read()
	feeds = json.loads(data)
	good = {}
	for key, feed in feeds.iteritems():
		try:
			doc = {'rss_id':feed['_id']}
			success, error = 0, 0
			print feed['url']
			for article in mongo.article.find(doc, timeout=False).limit(5):
				print article['title'], article['link']
			raw = raw_input("is del (y/n): ")
			if raw != 'y':
				good[key] = feed
		except KeyboardInterrupt, e:
			break
		except Exception, e:
			print e
	with open(conf.data_root + os.sep + 'best.json', 'w+') as fd:
		fd.write(json.dumps(good))

@cmd('sync-rss')
def sync_rss():
	mongo = MongoWeb(conf.mongo_web)
	with open(conf.data_root + os.sep + 'best.json') as fd:
		data = fd.read()
	feeds = json.loads(data)
	articles = mongo.article.find(timeout=False)
	k = 0
	for article in articles:
		if 'rss_id' not in article or article['rss_id'] not in feeds:
			mongo.article.remove({'_id':article['_id']})
		print k
		k += 1
	print 'sync index'
	index = mongo.index.find(timeout=False)
	for i in index:
		if not mongo.article.find_one({'_id':i['_id']}):
			mongo.index.remove({'_id':i['_id']})


@cmd('sync-oss')
def sync_oss():
	mongo = MongoSpider(conf.mongo_spider)
	with open(conf.data_root + os.sep + 'filter.json') as fd:
		data = fd.read()
	feeds = json.loads(data)
	feeds = dict(filter(lambda x: x[1]['status'] == 'good', feeds.iteritems()))
	for key, feed in feeds.iteritems():
		try:
			doc = {'rss_id':feed['_id'], 'html':{'$exists':True, '$ne':''}, 'oss':{'$ne':'success'}}
			success, error = 0, 0
			for article in mongo.article.find(doc, timeout=False):
				html = mongo.file.get(article['html'])
				html = html.encode('utf-8')
				if html and mongo.oss.put(article['html'], html):
					mongo.article.update({'_id':article['_id']}, {'$set':{'oss':'success'}})
					print article['title'], 'OK'
					success += 1
				else:
					mongo.article.update({'_id':article['_id']}, {'$set':{'oss':'error'}})
					print article['title'], 'Error'
					error += 1
			print key, success + error, success, error, feed['url']
		except KeyboardInterrupt, e:
			break
		except Exception, e:
			print e


# @auto_work('downrss', count=100)
# class DownRss(GeventWorker):
# 	""" download rss xml """

# 	def __init__(self, count=20):
# 		""" init class """
# 		super(DownRss, self).__init__(count)
# 		self.mongo = MongoAdmin(conf.mongo_spider)
# 		doc = {'$or': [{'xml': ''}, {'xml': {'$exists': False}}]}
# 		self.init_tasks(self.mongo.rss.find(doc, timeout=False))

# 	def handle(self, index, rss):
# 		""" download a rss """
# 		try:
# 			xml = get(rss['url'])
# 			self.mongo.file.put(rss['_id'] + '.xml', xml)
# 			self.mongo.rss.update({'_id':rss['_id']}, {'$set':{'xml':rss['_id'] + '.xml'}})
# 			print 'update[%d]: %d %s' % (index, len(xml), rss['url'])
# 		except KeyboardInterrupt, e:
# 			self.exit()
# 		except Exception, e:
# 			self.mongo.rss.update({'_id':rss['_id']}, {'$set':{'xml':e.__class__.__name__}})
# 			print e


@auto_work('score-rss', log=logger('score-rss', level=logging.INFO))
class ScoreRss(Worker):
	""" calculater rss score """

	def __init__(self, log):
		super(ScoreRss, self).__init__()
		self.log = log
		self.mongo = MongoSpider(conf.mongo_spider)
		self.article = self.mongo.article
		self.file = self.mongo.file
		with open(conf.data_root + os.sep + 'rss.json') as fd:
			data = fd.read()
		self.init_tasks(json.loads(data).values())
		self.out = {}

	def score_article(self, xart, yart):
		score = 0
		st, en = False, False
		xtitle, ytitle = xart['title'].strip(), yart['title'].strip()
		for i in range(min(len(xtitle), len(ytitle))):
			if not st and xtitle[i] == ytitle[i]:
				score += 1
			else:
				st = True
			if not en and xtitle[-i] == ytitle[-i]:
				score += 1
			else:
				en = True
			if en and st:
				break
		return score

	def score(self, articles):
		if not articles:
			return 0
		score = 0
		for i in range(len(articles)):
			for j in range(i+1, len(articles)):
				score += self.score_article(articles[i], articles[j])
		return score * 1.0 / ((len(articles) + 1) * len(articles) / 2)

	def score_time(self):
		return 0

	def bad(self, rss):
		res = urlparse.urlparse(rss['url'])
		params = dict([(k,v[0]) for k,v in urlparse.parse_qs(res.query).items()])
		if len(params) > 3:
			return True
		if '.gov.' in res.netloc or '.edu.' in res.netloc:
			return True
		if rss['language'] != 'zh':
			return True

	def filter(self, articles):
		return False

	def handle(self, index, rss):
		if self.bad(rss):
			#self.log.info('bad-rss: %s' % rss['url'])
			rss['status'] = 'bad'
			self.out[rss['_id']] = rss
			return
		try:
			articles = list(self.article.find({'rss_id':rss['_id']}))
			if len(articles) < 10:
				self.log.info('bad rss: %s' % rss['url'])
				rss['status'] = 'bad'
				self.out[rss['_id']] = rss
				return
			score = self.score(articles[:10])
			bad = self.filter(articles[:100])
			time_score = self.score_time(articles)

			rss['status'] = 'good'
			if score > 1 or bad:
				rss['status'] = 'bad'
			rss['score'] = score
			self.out[rss['_id']] = rss
			self.log.info('score[%d]: %d %6.3f %d %s' 
				% (index, len(self.out), score, len(articles), rss['url']))
		except Exception, e:
			self.log.warn('exception: %d %s %s' % (index, rss['url'], str(e)))
			pass

	def on_exit(self):
		self.log.info('wirte json start ...')
		with open(conf.data_root + os.sep + 'filter.json', 'w+') as fd:
			fd.write(json.dumps(self.out))
		self.log.info('write json end ...')