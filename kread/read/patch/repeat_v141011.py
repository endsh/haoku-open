# coding: utf-8
from collections import defaultdict
from utils import load_json
from .base import spider, find2do
from .cmd import *


def handle(repeat):
	return spider.article.find_one(
		{'_id':repeat['_id']}, {'tpl':1, 'url':1})


@remote('repeat_v141011')
def get_tpls():
	articles = find2do(spider.repeat, {'keys':[], 'repeat':True}, handle)

	tpls = defaultdict(list)
	for article in articles.itervalues():
		if len(tpls[article['tpl']]) < 10:
			tpls[article['tpl']].append(article['url'])

	return tpls

@local()
def handle_tpls():
	tpls = load_json('patch/repeat_v141011.json')
	print len(tpls)


if __name__ == '__main__':
	main()
