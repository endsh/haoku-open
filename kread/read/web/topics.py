# coding: utf-8
from flask import Blueprint, request, redirect, render_template
from flask import abort, url_for, jsonify
from accounts.sdk.sso import current_user
from .core import good_hots

bp = Blueprint('topics', __name__)

@bp.route('')
def old_topic_view():
	word = request.args.get('word')
	return topic_view(word)


@bp.route('/<string:word>.html')
def topic_view(word):
	last = request.args.get('last')
	limit = request.args.get('limit', 20, int)
	ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

	res = current_user.read.topic(word, last=last, limit=limit, hots=not ajax)
	if res['code'] != 0:
		abort(404)

	count = len(res['articles'])
	if res['articles'] and res['last'] != 0:
		url = url_for('.topic_view', word=word, last=res['last'], limit=limit)
	else:
		url = ''

	if ajax:
		html = render_template('topics/ajax.html', 
			word=word,
			articles=res['articles'],
		)
		return jsonify(dict(code=0, html=html, url=url))

	res['hots'] = good_hots(res['hots'])
	return render_template('topics/topic.html', 
		word=word,
		articles=res['articles'], 
		hots=res['hots'],
		load_url=url,
		count=res['count'],
	)


@bp.route('/<string:word>-<int:page>.html')
def topic_page(word, page):
	res = current_user.read.topic_page(word, page=page)
	if res['code'] != 0:
		abort(404)

	return render_template('topics/topic-page.html', 
		word=word,
		articles=res['articles'], 
		hots=res['hots'],
		page=page,
		count=res['count'],
	)
