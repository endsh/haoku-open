# coding: utf-8
import conf
import json
import math
import redis
from collections import defaultdict, OrderedDict
from db import MongoWeb, MongoSpider
from utils import print_dict


class Cluster(object):

	def __init__(self, conf):
		self.conf = conf
		self.web = MongoWeb(conf.mongo_web)
		self.spider = MongoSpider(conf.mongo_spider)
		self.redis = redis.Redis(**conf.redis_tag)

	def load_word(self, word):
		index = self.web.index.find(word)
		if index is None:
			print '%s is None' % word
			return

		print 'load word: %s' % word,
		
		tags = defaultdict(int)
		for article in index['index']:
			row = self.spider.keyword.find_one({'_id':article['i']})
			if row is not None:
				row['words'] = json.loads(row['words'])
				for word, _ in sorted(row['words']['index'].iteritems(), key=lambda x: -x[1])[:10]:
					tags[word] += 1

		print len(tags)

		return tags

	def update(self, tags, subs):
		if not subs:
			return
		subs = dict(filter(lambda x: x[1] >= 3, subs.iteritems()))
		for tag, cnt in subs.iteritems():
			tags[tag.lower()] += math.log(cnt, 10)

	def load_words(self, words, xmin=2):
		tags = defaultdict(int)
		for word in words:
			self.update(tags, self.load_word(word))
		return dict(filter(lambda x: x[1] >= xmin, tags.iteritems()))

	def run(self):
		res = {}
		from simin import SIMIN
		for topic, words in SIMIN.iteritems():
			words = words.split('|')
			tags = self.load_words(words)
			print_dict(tags, cmp_key=lambda x: -x[1])
			words = tags.keys()
			print '|'.join(OrderedDict(sorted(tags.iteritems(), key=lambda x: -x[1])).keys())
			tags = self.load_words(words)
			print_dict(tags, cmp_key=lambda x: -x[1])
			print '|'.join(OrderedDict(sorted(tags.iteritems(), key=lambda x: -x[1])).keys())
			res[topic] = tags
		return res

	def main(self):
		res = {}
		from simin import SIMIN
		for topic, words in SIMIN.iteritems():
			words = words.split('|')
			print topic
			res[topic] = {}
			for word in words:
				index = self.web.index.find(word)
				if index is None:
					continue
				if len(index['index']) > 100 and index['icon']:
					res[topic][word] = len(index['index'])
			res[topic] = OrderedDict(sorted(res[topic].iteritems(), key=lambda x: -x[1]))
			print_dict(res[topic], cmp_key=lambda x: -x[1])
			print '|'.join(res[topic].keys())
		return res

	def test_word(self, word):
		tags = self.load_word(word)
		tags = dict(filter(lambda x: x[1] >= 5, tags.iteritems()))
		print_dict(tags, cmp_key=lambda x: -x[1])
		words = tags.keys()
		tags = self.load_words(words, 3)
		print_dict(tags, cmp_key=lambda x: -x[1])
		words = tags.keys()
		tags = self.load_words(words, 4)
		print_dict(tags, cmp_key=lambda x: -x[1])
		return tags

	def test(self):
		res = {}
		res[u'小米'] = self.test_word(u'小米')
		res[u'雷军'] = self.test_word(u'雷军')
		res[u'魅族'] = self.test_word(u'魅族')
		res[u'iphone'] = self.test_word(u'iphone')
		res[u'苹果'] = self.test_word(u'苹果')
		res[u'乔布斯'] = self.test_word(u'乔布斯')
		return res


def get_topics():
	cluster = Cluster(conf)
	return cluster.run()


def test_topic():
	cluster = Cluster(conf)
	return cluster.main()


if __name__ == '__main__':
	get_topics()
