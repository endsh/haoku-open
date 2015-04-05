# coding: utf-8
import json
from flask import Blueprint, request, redirect, render_template
from flask import abort, url_for, jsonify, current_app
from accounts.sdk.sso import current_user

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
	res = current_user.read.index()
	if res['code'] != 0:
		current_app.logger.error('error: %s' % json.dumps(res))
		abort(404)

	for topic in res['topics']:
		topic['load_url'] = url_for('topics.topic_view', 
			word=topic['cate'], last=topic['last'], limit=10)

	return render_template('home/index.html',
		articles=res['articles'],
		topics=res['topics'],
		hots=res['hots'],
		keywords=res['keywords'],
	)


@bp.route('/cates')
def cates():
	res = current_user.read.cates()
	return render_template('home/cates.html', cates=res['cates'])


@bp.route('/latest')
def latest():
	last = request.args.get('last')
	limit = request.args.get('limit', 20, int)
	ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

	res = current_user.read.latest(last=last, limit=limit, hots=not ajax)
	if res['code'] != 0:
		abort(404)

	count = len(res['articles'])
	if res['articles'] and res['last'] != 0:
		url = url_for('.latest', last=res['last'], limit=limit)
	else:
		url = ''

	if ajax:
		html = render_template('home/latest-ajax.html', 
			articles=res['articles'],
		)
		return jsonify(dict(code=0, html=html, url=url))
	
	return render_template('home/latest.html',
		articles=res['articles'], 
		hots=res['hots'],
		keywords=res['keywords'],
		load_url=url,
	)