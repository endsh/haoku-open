# coding: utf-8
import conf
import redis
from .cmd import *

redis_word = redis.Redis(**conf.redis_word)
conf.redis_word['host'] = 'formatter.org'
conf.redis_word['db'] = 0
redis_word_new = redis.Redis(**conf.redis_word)


def save_words(key):
	print 'load %s' % key
	count = 0
	for hkey in redis_word.hkeys(key):
		redis_word_new.hset(key, hkey, redis_word.hget(key, hkey))
		count += 1
		if count % 10000 == 0:
			print count
	print 'save %s len: %d' % (key, count)
	redis_word.delete(key)


@remote()
def save():
	for a in '0123456789abcdef':
		for b in '0123456789abcdef':
			save_words(a + b)
	redis_word_new.set('total', redis_word.get('total'))
	redis_word.delete('total')


if __name__ == '__main__':
	main()
