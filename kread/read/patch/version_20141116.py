# coding: utf-8
from gevent import monkey; monkey.patch_socket()
import conf
import gevent.pool
from .base import find2do, spider
from .cmd import *

pool = gevent.pool.Pool(1000)

def update_version(article):
	version = sum(article['v'].values())
	pool.spawn(spider.article.update, {'_id':article['_id']}, {'$set':{'version':version}})


@remote()
def update():
	find2do(spider.article, {}, update_version, fields={'v':1})


if __name__ == '__main__':
	main()
