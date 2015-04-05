# coding: utf-8
from utils import get, get_or_cache, tag2text, clean_html, html2urls
from utils import get_path, print_dict
from collections import defaultdict

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


cates = u'新闻|科技|数码|娱乐|体育|军事|教育|财经|旅游|文化|历史|时尚|女性|汽车|房产|家居|公益|佛学|游戏|摄影|图片'.split('|')


def url2meta(url, get=get):
	try:
		html = get(url)
	except ValueError:
		return None
	return html2meta(html, url)


def html2meta(html, url):
	doc = clean_html(html, url, return_doc=True)
	return doc2meta(doc, url)


def doc2meta(doc, url):
	keywords = tag2text(doc, 'meta', name='keywords')
	keywords = keywords.replace(u'，', ',')
	if ',' in keywords:
		keywords = [x.strip() for x in keywords.split(',')]
	elif '|' in keywords:
		keywords = [x.strip() for x in keywords.split('|')]
	elif '_' in keywords:
		keywords = [x.strip() for x in keywords.split('_')]
	elif keywords.count(' ') > 2:
		keywords = [x.strip() for x in keywords.split(' ')]
	else:
		keywords = [keywords]
	keywords = filter(lambda x: x, keywords)
	return {
		'title': tag2text(doc, 'title'),
		'keywords': keywords,
		'favicon': tag2text(doc, 'link', rel='shortcut icon'),
		'rss': tag2text(doc, 'link', type='application/rss+xml', bad='comment'),
	}


def debug(url):
	print '=' * 100
	print 'url: %s' % url
	for key, value in url2meta(url, get=get_or_cache).iteritems():
		if isinstance(value, list):
			value = ' | '.join(value)
		print '%s: %s' % (key, value)


def debug_urls():
	debug('http://www.cnblogs.com/bluescorpio/archive/2010/05/31/1748503.html')
	debug('http://www.qq.com/')
	debug('http://www.yixieshi.com/')
	debug('http://www.baidu.com/')
	debug('http://www.xinhuanet.com/')
	debug('http://www.people.com.cn/')
	debug('http://www.cnblogs.com/')
	debug('http://www.csdn.net/')
	debug('http://www.36kr.com/')
	debug('http://www.huxiu.com/')
	debug('http://www.techweb.com.cn/')
	debug('http://www.cyzone.cn/')
	debug('http://www.51cto.com/')
	debug('http://www.hexun.com/')
	debug('http://www.iteye.com/')
	debug('http://www.163.com/')
	debug('http://www.sina.com.cn/')
	debug('http://www.tech2ipo.com/')


def test(url):
	html = get_or_cache(url)
	urls = html2urls(html, url, name=False)

	words = defaultdict(int)
	u = set()
	for i in urls:
		if i.startswith(url) and len(get_path(i).split('/')) <= 2:
			u.add(i)

	if len(u) < 10:
		for i in urls:
			if i.startswith(url) and len(get_path(i).split('/')) <= 3:
				u.add(i)

		if len(u) < 20:
			for i in urls:
				if i.startswith(url) and len(get_path(i).split('/')) <= 4:
					u.add(i)

	urls = list(u)[:10]

	for i in urls:
		res = url2meta(i, get=get_or_cache)
		if res is not None:
			if '_' in res['title']:
				for word in res['title'].split('_'):
					if word.strip():
						words[word.strip()] += 1
			elif '|' in res['title']:
				for word in res['title'].split('|'):
					if word.strip():
						words[word.strip()] += 1
			elif '-' in res['title']:
				for word in res['title'].split('-'):
					if word.strip():
						words[word.strip()] += 1
	print_dict(words, cmp_key=lambda x: -x[1], limit=5)


if __name__ == '__main__':
	test('http://www.dongxipuzi.com/')
	test('http://www.qq.com/')
	test('http://www.yixieshi.com/')
	test('http://www.baidu.com/')
	test('http://www.xinhuanet.com/')
	test('http://www.people.com.cn/')
	test('http://www.cnblogs.com/')
	test('http://www.csdn.net/')
	test('http://www.36kr.com/')
	test('http://www.huxiu.com/')
	test('http://www.techweb.com.cn/')
	test('http://www.cyzone.cn/')
	test('http://www.51cto.com/')
	test('http://www.hexun.com/')
	test('http://www.iteye.com/')
	test('http://www.163.com/')
	test('http://www.sina.com.cn/')
	test('http://www.tech2ipo.com/')
