# coding: utf-8
from gevent import monkey; monkey.patch_socket()
import conf
import gevent.pool
import json
import redis
import sys
from utils import unicode2hash
from .base import spider, find2do
from .cmd import *

redis_word = redis.Redis(**conf.redis_word)
pool = gevent.pool.Pool(100)

def _upgrade_word(row):
	row['words'] = json.loads(row['words'])
	spider.word_file.put(row['_id'], json.dumps({
		'sim': row['sim'],
		'words': row['words'],
	}))

	if row['sim'] == True:
		words = row['words']
		for word, cnt in words['all'].iteritems():
			word = word.lower()
			hkey = unicode2hash(word)
			key = hkey % 500
			redis_word.hincrby(key, hkey, 1)

	redis_word.incr('total', 1)


def upgrade_word(row):
	pool.spawn(_upgrade_word, row)


@remote()
def upgrade(skip=None, limit=None):
	if skip is not None:
		skip = int(skip) * 10000
	if limit is not None:
		limit = int(limit) * 10000
	find2do(spider.word, {}, upgrade_word, skip=skip, limit=limit)


if __name__ == '__main__':
	main()
