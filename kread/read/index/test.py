# coding: utf-8
import conf
import json
import math
import redis
import hashlib
import pymongo
from collections import OrderedDict, defaultdict
from db import MongoSpider
from utils import print_dict, cache_key


redis_word = redis.Redis(**conf.redis_word)
mongo = MongoSpider(conf.mongo_spider)


def tags(key, words, out, main, loo):

	res = {}
	total = sum([x for x in words.itervalues()])
	words_cnt = len(words)
	for word, cnt in words.iteritems():
		if len(word) <= 1 or len(word) >= 8:
			continue
		score = int(redis_word.hget(hashlib.md5(word.encode('utf-8')).hexdigest()[:2], word))
		try:
			res[word] = min(len(word), 4) ** 0.5 * cnt ** 0.8 / (total ** 1.5 / words_cnt) * math.log10(100000.0 / (score + 1))
		except:
			pass
	res = OrderedDict(sorted(res.iteritems(), key=lambda x: -x[1])[:60])

	i = 0
	for w, s in res.iteritems():
		loo[w] += 1
		i += 1
		if i > 5:
			break

	for w, s in res.iteritems():
		main[key].append(w)

	for w, s in res.iteritems():
		out[w].append(key)


def base_cluster(count):
	doc = {'repeat':True}
	articles = mongo.repeat.find(doc).limit(count)
	out = defaultdict(list)
	main = defaultdict(list)
	loo = defaultdict(int)
	i = 0
	for article in articles:
		words = json.loads(article['words'])['all']
		tags(article['_id'], words, out, main, loo)
		if i % 100 == 0:
			print i
		i += 1

	res = defaultdict(dict)
	cnt = dict()
	for w, x in out.iteritems():
		if len(x) < 5 or w not in loo:
			continue
		for k in x:
			for c in main[k]:
				if c == w:
					continue
				if c not in res[w]:
					res[w][c] = 0
				res[w][c] += 1
		res[w] = dict(filter(lambda x: x[1] > 1, res[w].iteritems()))
		if not res[w]:
			del res[w]
		else:
			cnt[w] = len(x)
	return {'res':res, 'cnt':cnt, 'loo':loo}


def main():
	a = cache_key('cluster-test', base_cluster, 100000)
	res, cnt, loo = a['res'], a['cnt'], a['loo']

	b = 0
	q = {}
	for w, v in res.iteritems():
		#v = dict(filter(lambda x: x[1] > 1, v.iteritems()))
		# if b >= 10000:
		# 	break
		# b += 1
		if loo[w] < 10:
			continue

		v = dict(filter(lambda x: x[1] > 5, res[w].iteritems()))
		q[w] = cnt[w]
		if v:
			print_dict(v, title='word: %s %d' % (w, cnt[w]), cmp_key=lambda x: x[1])

	print_dict(q, cmp_key=lambda x: x[1])

	# global out
	# out = OrderedDict(filter(lambda x: x[1] > 5, sorted(out.iteritems(), key=lambda x: -x[1])))
	# print_dict(out)
	# print len(out)


if __name__ == '__main__':
	main()
