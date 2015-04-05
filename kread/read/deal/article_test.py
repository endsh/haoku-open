# coding: utf-8
import json
from flask import request
from utils import web_route, web_static, atime
from utils import get_or_cache, fetch_urls
from utils import get_test_urls, add_test_url
from deal.article import ArticleExtractor, ArticleMerger, ArticleNotFound


web_static('/article', 'article', u'文章', historys=get_test_urls)


@web_route('/article/all')
@atime('test article all')
def test_article_all():
	urls = get_test_urls()
	res = []
	for url in urls:
		try:
			html = get_or_cache(url)
		except:
			continue

		try:
			extractor = ArticleExtractor(html, url)
			res.append({
				'url':url, 
				'article':extractor.article, 
				'selector':extractor.selector,
			})
		except ArticleNotFound, e:
			print url
			print str(e)
			continue
	print '-' * 80
	print len(urls)
	return json.dumps(res)


@web_route('/article/')
@atime('test article')
def test_article():
	debug = True if request.args.get('debug') == 'true' else False
	url = request.args.get('url', '')
	if not url.startswith('http://'):
		return 'url is not startswith http://'
	add_test_url(url)
	html = get_or_cache(url, print_path=True)
	extractor = ArticleExtractor(html, url, debug=debug)
	article = extractor.article
	selector = extractor.selector
	if extractor.pages and article:
		article['content'] = ArticleMerger(
			url,
			extractor.title, 
			fetch_urls(extractor.pages, handle=get_or_cache),
			debug=debug,
			**selector
		).content
	return json.dumps({'url':url, 'article':article, 'selector':selector})
