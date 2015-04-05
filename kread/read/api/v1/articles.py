# coding: utf-8
import time
import random
from flask import request
from flask.ext.restful import abort, Resource, reqparse
from simin.web.api import strip
from accounts.sdk.access import current_user
from utils import time2best
from .core import access, api, mongo, cache, img2url, tag2icon, tags2icon
from .core import find_article, get_hots, get_keywords
from .contant import *


@cache.memoize(timeout=120)
def get_comments(id, page):
	res = mongo.comment.find(id, page - 1)
	if res is None or not res['comments']:
		return None

	profiles = current_user.accounts.profiles([x['uid'] for x in res['comments']])
	if profiles is None:
		return None

	profiles = dict((int(x), y) for x, y in profiles['profiles'].iteritems())

	comments = []
	num = (page - 1) * 10
	for comment in res['comments']:
		num += 1
		comments.append({
			'uid': comment['uid'],
			'nickname': profiles[comment['uid']]['nickname'],
			'avatar': profiles[comment['uid']]['avatar'],
			'content': comment['content'],
			'pubdate': time2best(comment['pubtime']),
			'num': num,
		})

	return list(reversed(comments))


class Article(Resource):

	def get(self, id):
		res = self.common(id)
		res['count'] = mongo.comment.count(id)

		if res['count']['comments'] > 0:
			page = (res['count']['comments'] + 9) / 10
			res['comments'] = get_comments(id, page)
			if res['count']['comments'] % 10 < 5 and page > 1:
				page -= 1
				res['comments'].extend(get_comments(id, page))
			res['comment_page'] = page - 1
		else:
			res['comments'] = []
			res['comment_page'] = 0

		res['hots'] = get_hots(random.randint(0, 50))
		res['keywords'] = get_keywords(random.randint(0, 50))
		return res

	@cache.memoize(timeout=300)
	def common(self, id):
		article = find_article({'id':id})
		if article is None:
			abort(API_NOT_FOUND)

		# key = random.choice(article['icons'].keys())
		# article['icon'] = img2url(article['icons'][key]['path'])
		article['text'] = mongo.text_file.get(article['content'])
		article['pubdate'] = time2best(article['pubtime'])
		tags = tags2icon(article['tags'])

		return dict(article=article, tags=tags)


class PostComment(Resource):

	def __init__(self):
		super(PostComment, self).__init__()
		self.req = reqparse.RequestParser()
		self.req.add_argument('content', type=unicode, required=True)	

	def post(self, id):
		current_user.access_user()
		args = self.req.parse_args()
		args = strip(args)
		if not args['content']:
			abort(INVALID_ARGS)

		row = dict(content=args['content'], uid=current_user.uid, pubtime=time.time())
		total = mongo.comment.add(id, row)

		cache.delete_memoized(get_comments, id, (total + 9) / 10)

		profiles = current_user.accounts.profiles(current_user.uid)
		if profiles is None:
			return abort(INVALID_ARGS)

		profiles = dict((int(x), y) for x, y in profiles['profiles'].iteritems())
		comment = {
			'nickname': profiles[row['uid']]['nickname'],
			'avatar': profiles[row['uid']]['avatar'],
			'content': row['content'],
			'pubdate': time2best(row['pubtime']),
			'num': total + 1,
		}
		return dict(comment=comment)


@access.public
class Comments(Resource):

	def get(self, id):
		page = request.args.get('page', -1, int)
		if page < 0:
			abort(API_NOT_FOUND)

		comments = get_comments(id, page)
		if not comments:
			abort(API_NOT_FOUND)
		return dict(comments=comments, next=page - 1)	


api.add_resource(Article, '/articles/<string:id>/')
api.add_resource(PostComment, '/articles/<string:id>/post-comment')
api.add_resource(Comments, '/articles/<string:id>/comments')