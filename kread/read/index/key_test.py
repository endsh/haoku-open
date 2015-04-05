# coding: utf-8
import conf
import json
import redis
from db import MongoSpider
from utils import print_list, print_dict
from index.key import Keyword

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def main():
	mongo = MongoSpider(conf.mongo_spider)
	redis_word = redis.Redis(**conf.redis_word)
	keyword = Keyword(redis_word)

	for article in mongo.article.find({'v.seg':{'$gt':0}}).skip(1000).limit(10):
		if article is None or article['v']['seg'] <= 0:
			continue
		word = mongo.word_file.get(article['_id'])
		if word is not None:
			word = json.loads(word)

		title = article['title']
		words = word['words']
		res = keyword.make(title, words)
		if res is not None:
			print
			print
			print
			print '*' * 100
			print 'http://www.haoku.net/articles/%s.html' % article['_id']
			print_list(res['keys'], title='keys of %s' % title)
			print_dict(res['words'], title='index of %s' % title, cmp_key=lambda x: -x[1])


if __name__ == '__main__':
	main()