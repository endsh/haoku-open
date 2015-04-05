# coding: utf-8
import conf
import redis
from .cmd import *

redis_tag = redis.Redis(**conf.redis_tag)
conf.redis_tag['host'] = '51ku.net'
conf.redis_tag['db'] = 0
redis_tag_new = redis.Redis(**conf.redis_tag)


def save_words(key):
	print 'load %s' % key
	count = 0
	for hkey in redis_tag.hkeys(key):
		redis_tag_new.hset(key, hkey, redis_tag.hget(key, hkey))
		count += 1
		if count % 10000 == 0:
			print count
	print 'save %s len: %d' % (key, count)
	redis_tag.delete(key)


@remote()
def save():
	for a in '0123456789abcdef':
		for b in '0123456789abcdef':
			save_words(a + b)
	redis_tag_new.set('total', redis_tag.get('total'))
	redis_tag.delete('total')
	redis_tag_new.set('version', redis_tag.get('version'))
	redis_tag.delete('version')
	redis_tag_new.set('last', redis_tag.get('last'))
	redis_tag.delete('last')


if __name__ == '__main__':
	main()
