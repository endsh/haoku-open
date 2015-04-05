# coding: utf-8
from collections import defaultdict
from utils import load_json
from .base import spider, find2do, redis_word
from .cmd import *


@remote()
def upgrade():
	print 'update article'
	spider.article.update({}, {'$set':{'sim':False, 'v.sim':0}}, False, True)
	print 'remove repeat'
	spider.conn.read['repeat'].drop()

	print 'clear word redis'
	redis_word.flushdb()


if __name__ == '__main__':
	main()
