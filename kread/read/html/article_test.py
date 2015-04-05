# coding: utf-8
import json
from flask import request
from utils import web_route, web_static, atime
from utils import get_or_cache, fetch_urls
from utils import get_test_urls, add_test_url
from html.article import Article

web_static('/article', 'article', u'文章', historys=get_test_urls)


@web_route('/article/all')
@atime('test article all')
def test_article_all():
	urls = get_test_urls()
	res = []
	for url in urls:
		try:
			html = get_or_cache(url)
			extractor = Article(html, url)
			res.append({
				'url':url, 
				'article':extractor.article, 
				'selector':extractor.selector,
			})

			from utils import print_dict
			print_dict(extractor.article)
			print_dict(extractor.selector)
		except:
			print 'error', url
	print '-' * 80
	print len(urls)
	return json.dumps(res)


@web_route('/article/<path:url>')
@atime('test article')
def test_article(url):
	debug = True if request.args.get('debug') == 'true' else False
	url = url.split('#')[0].split('?')[0]
	if not url.startswith('http://'):
		return 'url is not startswith http://'
	add_test_url(url)
	html = get_or_cache(url)
	extractor = Article(html, url, debug=debug)
	article = extractor.article
	selector = extractor.selector

	from utils import print_dict
	print_dict(article)
	print_dict(selector)
	# if extractor.pages:
	# 	article['content'] = ArticleMerger(
	# 		url,
	# 		extractor.title, 
	# 		fetch_urls(extractor.pages, handle=get_or_cache),
	# 		debug=debug,
	# 		**selector
	# 	).content
	return json.dumps({'url':url, 'article':article, 'selector':selector})
