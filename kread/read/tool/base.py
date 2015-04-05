# coding: utf-8
import conf
from db import MongoSpider, MongoWeb

spider = MongoSpider(conf.mongo_spider)
web = MongoWeb(conf.mongo_web)


def find2do(table, doc, handle):
	res = {}
	count = 0
	for x in table.find(doc):
		y = handle(x)
		if y is not None:
			res[x['_id']] = y
		count += 1
		if count % 1000 == 0:
			print count

	return res
