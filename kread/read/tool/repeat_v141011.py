# coding: utf-8
from collections import defaultdict
from .base import spider, find2do
from .cmd import remote


def handle(repeat):
	return spider.article.find_one(
		{'_id':repeat['_id']}, {'tpl':1, 'url':1})


@remote('repeat_v141011')
def get_tpls():
	articles = find2do(spider.repeat, {'keys':[], 'repeat':True})

	tpls = defaultdict(list)
	for article in articles.itertiems():
		if len(tpls[article['tpl']]) < 10:
			tpls.append(article['url'])

	return res


if __name__ == '__main__':
	main()
