#coding: utf-8
import sys
from flask import Blueprint, request, render_template, abort, jsonify
from core import mongo_iweb
from utils import html2text
from simhash import Simhash

bp = Blueprint('distance', __name__)

def testjsonify(res):
	print res
	return jsonify(res)



@bp.route('/', methods=["POST", "GET"])
def index():
	return render_template('distance/index.html')

@bp.route('/calc', methods=["POST", "GET"])
def calc():
	res = {'code': 1}
	id1 = request.args.get('_id1', '')
	id2 = request.args.get('_id2', '')
	if not id1 or not id2:
		res['msg'] = 'article id was null'
		return testjsonify(res)

	article1 = mongo_iweb.spider_article.find_one({'_id':id1})
	article2 = mongo_iweb.spider_article.find_one({'_id':id2})
	if not article1 or not article2:
		res['msg'] = 'article id was error'
		return testjsonify(res)
	try:
		text1 = article1['title'] + html2text(article1['content'])
		num1 = Simhash(text1).value - sys.maxint

		text2 = article2['title'] + html2text(article2['content'])
		num2 = Simhash(text2).value - sys.maxint

		distance = mongo_iweb.sim.distance(num1, num2)
	except Exception, e:
		res['msg'] = str(e)
		return testjsonify(res)
	res['code'] = 0
	res['distance'] = distance
	return testjsonify(res)