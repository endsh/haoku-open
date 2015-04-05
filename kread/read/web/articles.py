# coding: utf-8
import time
from flask import Blueprint, request, redirect, render_template
from flask import abort, url_for, jsonify
from accounts.sdk.sso import current_user
from utils import time2best
from .forms import CommentForm
from .core import good_hots

sp = Blueprint('old', __name__)
bp = Blueprint('articles', __name__)


@bp.route('/<int:date>/<int:id>.html')
def article_view(date, id):
	id = '%d%d' % (date, id)
	type = request.args.get('type')
	if type == 'comments':
		return comments(id)
	elif type == 'post-comment':
		return post_comment(id)
	elif type == 'post-like':
		return post_like(id)

	if request.method != 'GET':
		abort(403)

	res = current_user.read.article(id)
	if res['code'] != 0:
		abort(404)

	page = res['comment_page']
	load_url = url_for('.article_view', date=id[:8], id=id[8:], type="comments", page=page) if page > 0 else ''

	res['hots'] = good_hots(res['hots'])
	return render_template('articles/article.html', 
		article=res['article'], 
		count=res['count'],
		comments=res['comments'],
		load_url=load_url,
		tags=res['tags'], 
		hots=res['hots'],
	)


@sp.route('/<string:id>', methods=['GET', 'POST'])
def old_article_view(id):
	return redirect(url_for('.article_view', id=id, **request.args))


@sp.route('/<string:id>.html', methods=['GET', 'POST'])
def old_old_article_view(id):
	type = request.args.get('type')
	if type == 'comments':
		return comments(id)
	elif type == 'post-comment':
		return post_comment(id)
	elif type == 'post-like':
		return post_like(id)

	if request.method != 'GET':
		abort(403)

	res = current_user.read.article(id)
	if res['code'] != 0:
		abort(404)

	page = res['comment_page']
	load_url = url_for('.article_view', id=id, type="comments", page=page) if page > 0 else ''

	return render_template('articles/article.html', 
		article=res['article'], 
		count=res['count'],
		comments=res['comments'],
		load_url=load_url,
		tags=res['tags'], 
		hots=res['hots'],
	)
	

def comments(id):
	page = request.args.get('page', -1, int)

	res = current_user.read.comments(id, page)
	if res['code'] != 0:
		return jsonify(res)
	html = unicode(render_template('articles/comments.html', comments=res['comments']))

	page = res['next']
	load_url = url_for('.article_view', id=id, type="comments", page=page) if page > 0 else ''
	res = dict(code=0, html=html, url=load_url)
	return jsonify(res)

def post_comment(id):
	if not current_user.login:
		return jsonify(dict(code=-1, msg=u'请先登录'))

	form = CommentForm(request.form)
	if form.validate_on_submit():
		res = current_user.read.post_comment(id, form.content.data)
		return jsonify(res)

	abort(403)


def post_like(id):
	pass