# coding: utf-8
import sys
from htmldiff import render_html_diff
from flask import Blueprint, render_template, request, jsonify
from flask.ext.login import current_user, login_required
from ..core import mongo_admin
from ..account.models import Account
from simhash import Simhash
from conf import release
from db import MongoSpider
from utils import html2text

page_num = 15
simhash_mongo = mongo_admin.simhash
mongo_spider = MongoSpider(release.mongo_spider)
sim = mongo_spider.sim
article_mongo = mongo_spider.article
bp = Blueprint('test', __name__)


@bp.route('/simhash')
def simhash():
	p = request.args.get('p', 0, int)
	cursors = sim.sim.find({'ids':{"$nin": [{}]}}).skip(p * page_num).limit(page_num)
	res = []
	arts = []
	arts_like = []
	for cursor in cursors:
		cursor = dict(cursor)
		cursor['distance'] = mongo_spider.sim.distance(cursor['num'], cursor['ids'].values()[0])
		res.append(cursor)
		ids = cursor['ids'].keys()
		arts.extend(ids)
		arts.append(cursor['_id'])

	cursors = article_mongo.find({"_id":{"$in" : arts}}, {'title':1})
	arts = {}
	for cursor in cursors:
		arts[cursor['_id']] = cursor['title']
	return render_template('test/simhash.html', arts=arts, res=res, p=p)

default = 'KKKLLLMMMNNNOOO'
@bp.route('/distance')
def distance():
	data = request.args.get('data', '')
	title1 = request.args.get('title1', '')
	title2 = request.args.get('title2', '')
	data = eval(data)
	print data
	res = {'title1':title1, 'title2':title2}
	nums = data['ids'].values()
	for num in nums:
		res[u'原差距'] = mongo_spider.sim.distance(data['num'], num)
	
	title_num1 = Simhash(title1).value - sys.maxint
	title_num2 = Simhash(title2).value - sys.maxint
	res[u'标题差距'] = mongo_spider.sim.distance(title_num1, title_num2)

	article = article_mongo.find_one({'_id':data['_id']}, {'content':1, 'title':1})
	content_num1 = Simhash(article['content']).value - sys.maxint
	text_num = Simhash(article['title'] + default + html2text(article['content']) ).value - sys.maxint
	res['content1'] = article['content']

	cursors = article_mongo.find({"_id":{"$in" : data['ids'].keys()}}, {'content':1, 'title':1})
	for cursor in cursors:		
		content_num2 = Simhash(cursor['content']).value - sys.maxint
		text_num2 = Simhash(cursor['title'] + default + html2text(cursor['content'])).value - sys.maxint
		res[u'正文差距'] = mongo_spider.sim.distance(content_num1, content_num2)
		res[u'新差距'] = mongo_spider.sim.distance(text_num2, text_num )
		res['content2'] = cursor['content']


	d = render_html_diff(res['content1'], res['content2'])
	
	# result = list(d.compare(res['content1'], res['content2']))
	# res['res'] = ''.join(result.spilt('+'))
	# from pprint import pprint as _pprint
	# _pprint(result)
	res['d'] = d
	return render_template('test/detail.html', data=res)

@bp.route('/tests')
def tests():
	data = request.args.get('data', '')
	assert data is not None
	res, data = {}, eval(data)

	article = article_mongo.find_one({'_id':data['_id']}, {'content':1, 'title':1})
	cursors = article_mongo.find({"_id":{"$in" : data['ids'].keys()}}, {'content':1, 'title':1})
	for cursor in cursors:
		for i in xrange(1, 10):
			text_num1 = Simhash( default * i + article['title'] + html2text(article['content']) ).value - sys.maxint
			text_num2 = Simhash( default * i + cursor['title'] + html2text(cursor['content'])).value - sys.maxint
			
			text_num3 = Simhash(article['title'] + default * i + html2text(article['content']) ).value - sys.maxint
			text_num4 = Simhash(cursor['title'] + default * i + html2text(cursor['content'])).value - sys.maxint
			
			text_num5 = Simhash(article['title'] + html2text(article['content']) + default * i).value - sys.maxint
			text_num6 = Simhash(cursor['title'] + html2text(cursor['content']) + default * i).value - sys.maxint
			
			text_num7 = Simhash( default * i + article['title'] + default * i + html2text(article['content']) + default * i).value - sys.maxint
			text_num8 = Simhash( default * i + cursor['title'] + default * i + html2text(cursor['content']) + default * i).value - sys.maxint
			distance = mongo_spider.sim.distance
			res[i] = [distance(text_num1, text_num2), distance(text_num3, text_num4), distance(text_num5, text_num6), distance(text_num7, text_num8)]
	return render_template('test/tests.html', data=res)

@login_required
@bp.route('/errors')
def errors():
	sid = request.args.get('sid', '')
	uid = current_user.id
	assert sid is not None
	assert uid is not None
	if not sid or not uid:
		return jsonify({'code':1})
	try:
		simhash_mongo.save({'sid':sid, 'uid':uid})
	except Exception, e:
		return jsonify({'code':1})	
	return jsonify({'code':0})