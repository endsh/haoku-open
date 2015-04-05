# coding: utf-8
from gevent import monkey; monkey.patch_socket()
import pymongo
import conf
import gevent.pool
import json
import redis
import sys
import hashlib
import math
import urllib
from collections import OrderedDict
from index import Keyword
from utils import unicode2hash, hash2long, html2doc, doc2html
from .base import spider, find2do, iweb
from .cmd import *
from pymongo.errors import OperationFailure

redis_word = redis.Redis(**conf.redis_word)
redis_tag = redis.Redis(**conf.redis_tag)
redis_time = redis.Redis(**conf.redis_time)
redis_url = redis.Redis(**conf.redis_url)
keyword = Keyword(redis_word)

@remote()
def upgrade():
	iweb.index.drop()
	iweb.topic.drop()
	iweb.article.drop()
	iweb.spider_article.drop()
	iweb.spider_exc.drop()
	iweb.sim.drop()

	redis_tag.flushdb()
	redis_time.flushdb()
	redis_url.flushdb()

	iweb.index.create_index()
	iweb.topic.create_index()

	iweb.article.create_index([('id', pymongo.ASCENDING)])
	iweb.article.create_index([('long', pymongo.ASCENDING)])
	iweb.article.create_index([('pubtime', pymongo.DESCENDING)])
	iweb.sim.create_index()

	index = [
		[
			('id', pymongo.ASCENDING),
		],
		[
			('long', pymongo.ASCENDING),
		],
		[
			('f', pymongo.DESCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('domain', pymongo.ASCENDING),
			('f', pymongo.ASCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('v.seg', pymongo.DESCENDING),
		],
		[
			('version', pymongo.DESCENDING),
		],
		[
			('pubtime', pymongo.DESCENDING),
		]
	]

	for i in index:
		iweb.spider_article.create_index(i)

	index = [
		[
			('id', pymongo.ASCENDING),
		],
		[
			('long', pymongo.ASCENDING),
		],
		[
			('f', pymongo.DESCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('domain', pymongo.ASCENDING),
			('f', pymongo.ASCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('pubtime', pymongo.DESCENDING),
		]
	]

	for i in index:
		iweb.spider_exc.create_index(i)

	# # iweb.conn.admin.command('enablesharding', 'spider')
	# iweb.conn.admin.command('shardcollection', 'spider.article', keys={'_id':1})
	# iweb.conn.admin.command('shardcollection', 'spider.exc_article', keys={'_id':1})

	# # iweb.conn.admin.command('enablesharding', 'read')
	# iweb.conn.admin.command('shardcollection', 'read.article', keys={'_id':1})

	# # iweb.conn.admin.command('enablesharding', 'index')
	# iweb.conn.admin.command('shardcollection', 'index.index', keys={'word':1})
	# iweb.conn.admin.command('shardcollection', 'index.index_keys', keys={'_id':1})
	# iweb.conn.admin.command('shardcollection', 'index.topic', keys={'word':1})
	# iweb.conn.admin.command('shardcollection', 'index.topic_keys', keys={'_id':1})


if __name__ == '__main__':
	main()
