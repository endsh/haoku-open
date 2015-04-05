# coding: utf-8
from utils import load_json
from .base import spider, find2do
from .cmd import *


def handle(sim):
	print '=' * 100
	article = spider.article.find_one({'_id':sim['_id']})
	if article:
		print article['title'], article['url']
	for key in sim['ids']:
		article = spider.article.find_one({'_id':key})
		if article:
			print article['title'], article['url']


@local()
def get_sims():
	find2do(spider.conn.sim['sim'], {'ids':{'$ne':{}}}, handle)


if __name__ == '__main__':
	main()
