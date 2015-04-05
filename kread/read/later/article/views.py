# coding: utf-8
import re
import json
import time
import pymongo
from flask import Blueprint, request, render_template
from flask import redirect, url_for, abort
from deal import html2article
from utils import get_or_cache, get_domain, html2urls, url2tpl
from later.core import mongo

bp = Blueprint('article', __name__)


@bp.route('/')
def index():
	articles = list(mongo.article.find().sort('last', pymongo.DESCENDING).limit(10))
	for article in articles:
		article['pubtime'] = article['pubtime'][5:10]
	return render_template('extract/index.html', articles=articles)


@bp.route('/page')
@bp.route('/page/<int:page>')
def article_list(page=1):
	if page < 1:
		page = 1
	articles = mongo.article.find().sort('last', pymongo.DESCENDING).skip((page - 1) * 50).limit(50)
	count = articles.count()
	pages = (count + 49) // 50
	if page > pages:
		abort(404)

	articles = list(articles)
	for article in articles:
		article['pubtime'] = article['pubtime'][:10]
	return render_template('extract/list.html', articles=articles, page=page, pages=pages, count=count)


@bp.route('/article')
def article():
	url = request.args.get('url')

	article = mongo.article.find_one({'_id':url})

	if not article:
		try:
			html = get_or_cache(url)
			article = html2article(html, url, selector=True, merge=True)
			if article and not article['src_name']:
				article['src_name'] = get_domain(url)

			tpl = url2tpl(url)
			urls = html2urls(html, url)
			texts = dict(map(lambda x: (x[0], max(x[1], key=lambda y:len(y))), urls.iteritems()))
			tmp = dict(map(lambda x: (x, url2tpl(x)), texts.iterkeys()))

			urls = {}
			for u, t in tmp.iteritems():
				if u != url and t == tpl:
					urls[u] = texts[u]
					if len(urls) >= 10:
						break

			if article:
				article['urls'] = urls
				article['_id'] = url
				article['view'] = 1
				article['last'] = time.time()

				copy = article.copy()
				copy['urls'] = json.dumps(copy['urls'])
				mongo.article.save(copy)
		except:
			pass
	else:
		article['urls'] = json.loads(article['urls'])
		mongo.article.update({'_id':url}, {'$set':{'view':article['view'] + 1}})

	if article:
		article['pubtime'] = article['pubtime'][:10]

	return render_template('extract/article.html', article=article, url=url)
