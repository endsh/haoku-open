# coding: utf-8
import conf
import json
import math
import redis
from collections import defaultdict
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
			print '%s is None'
			return
		
		tags = defaultdict(int)
		for article in index['index']:
			row = self.spider.keyword.find_one({'_id':article['i']})
			if row is not None:
				row['words'] = json.loads(row['words'])
				for word, _ in sorted(row['words']['index'].iteritems(), key=lambda x: -x[1])[:5]:
					tags[word] += 1

		return tags

	def update(self, tags, subs):
		subs = dict(filter(lambda x: x[1] >= 5, subs.iteritems()))
		for tag, cnt in subs.iteritems():
			tags[tag.lower()] += math.log(cnt, 10)

	def load_words(self, words):
		tags = defaultdict(int)
		for word in words:
			self.update(tags, self.load_word(word))
		return dict(filter(lambda x: x[1] >= 2, tags.iteritems()))

	def run(self):
		words = u'小米|安卓|魅族|华为荣耀|HTC|iPhone|iPad|智能手机|智能硬件|ios|苹果|谷歌|三星|锤子|联想'.split('|')
		tags = self.load_words(words)
		print_dict(tags, cmp_key=lambda x: -x[1])
		words = tags.keys()
		tags = self.load_words(words)
		print_dict(tags, cmp_key=lambda x: -x[1])
		words = tags.keys()
		tags = self.load_words(words)
		print_dict(tags, cmp_key=lambda x: -x[1])


def main():
	cluster = Cluster(conf)
	cluster.run()


if __name__ == '__main__':
	main()