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

	def __init__(self, master):
		self.master = master
		self.topic = master.mongo.topic
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
		if cnt < 1:
			return

		xicons = [x['path'] for x in article['icons'].values()]
		self.topic.add(topic, article['long'], len(article['icons']), article['pubtime'], xicons)
		return topic
