# coding: utf-8
import json
from flask import request
from utils import web_route, web_static, atime
from utils import get_or_cache, fetch_urls
from utils import get_test_urls, add_test_url, html2text
from deal.article import ArticleExtractor, ArticleMerger
from index.segment import segmentor


web_static('/segment', 'segment', u'分词', historys=get_test_urls)


@web_route('/segment/all')
@atime('test segment all')
def test_segment_all():
	urls = get_test_urls()
	res = []
	for url in urls:
		html = get_or_cache(url)
		extractor = ArticleExtractor(html, url)
		content = extractor.content
		if extractor.pages:
			content = ArticleMerger(
				url, 
				extractor.title, 
				fetch_urls(extractor.pages, handle=get_or_cache),
				**extractor.selector
			).content
		res.append({
			'url':url, 
			'title': extractor.title,
			'words': segmentor.seg(extractor.title, html2text(content, code=False))
		})
	return json.dumps(res)


@web_route('/segment/<path:url>')
@atime('test segment')
def test_segment(url):
	url = url.split('#')[0].split('?')[0]
	if not url.startswith('http://'):
		return 'url is not startswith http://'
	add_test_url(url)
	html = get_or_cache(url)
	extractor = ArticleExtractor(html, url)
	content = extractor.content
	if extractor.pages:
		content = ArticleMerger(
			url, 
			extractor.title, 
			fetch_urls(extractor.pages, handle=get_or_cache),
			**extractor.selector
		).content
	return json.dumps({
		'url':url, 
		'title': extractor.title,
		'words': segmentor.seg(extractor.title, html2text(content))
	})
