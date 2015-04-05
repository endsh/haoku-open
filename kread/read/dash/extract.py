# coding: utf-8
import re
from flask import Blueprint, request, render_template
from dash.core import mongo_spider
import json
bp = Blueprint('extract', __name__)

@bp.route('/')
def index():
	pass


@bp.route('/page')
@bp.route('/page/<int:page>')
def article_list(page=1):
	pass

@bp.route('/article')
def article():
	_id = request.args.get('id')
	article = mongo_spider.article.find_one({'_id':_id})

	# article['urls'] = json.loads(article['urls'])

	if article:
		article['pubtime'] = article['pubtime'][:10]
	return render_template('extract/article.html', article=article, _id=_id, url=article['url'], tags=', '.join(article['tags']))
