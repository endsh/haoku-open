# coding: utf-8
import conf
import redis
from db import MongoSpider, MongoWeb, MongoIWeb

#spider = MongoSpider(conf.mongo_spider)
# web = MongoWeb(conf.mongo_web)
iweb = MongoIWeb(conf.mongo_iweb)
redis_word = redis.Redis(**conf.redis_word)
url_redis = redis.Redis(**conf.redis_url)


def find2do(table, doc, handle, fields=None, skip=None, limit=None):
	res = {}
	count = 0
	data = table.find(doc, fields, timeout=False)
	if skip is not None:
		data.skip(skip)
	if limit is not None:
		data.limit(limit)
	for x in data:
		y = handle(x)
		if y is not None:
			res[x['_id']] = y
		count += 1
		if count % 1000 == 0:
			print count

	return res


def find():
	pass