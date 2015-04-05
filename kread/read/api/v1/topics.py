# coding: utf-8
import random
from flask import current_app, request
from flask.ext.restful import Resource
from utils import time2best
from .core import api, cache, mongo, cates, topics, icon2url
from .core import find_article, find_topic, find_topic_page, find_articles
from .core import tags2icon, remove_index, get_hots, get_keywords


class Index(Resource):

	def get(self):
		res = self.common()
		res['hots'] = get_hots(random.randint(0, 50))
		res['keywords'] = get_keywords(random.randint(0, 50))
		return res

	def common(self):
		ids, tids = [], []
		for cate in cates:
			_, topic = find_topic(cate, limit=6)
			if topic is None:
				continue
			ids.extend(topic[:2])
			tids.append({'cate':cate, 'ids':topic[2:6]})

		articles, index = [], 0

		fields = {'id':1, 'long':1, 'title':1, 'icons':1}
		longs = [x['article'] for x in ids]
		arts = find_articles('long', longs, fields=fields)
		arts = dict((x['long'], x) for x in arts)
		for id in ids:
			if id['article'] not in arts:
				continue

			art = arts[id['article']]

			width, height = 230, 130
			if index == 0:
				width, height = 500, 300
			elif index == 11:
				width, height = 285, 248

			index += 1

			val = random.choice(art['icons'].values()) if art['icons'] else None
			icon = icon2url(val, width, height) if val is not None else ''

			article = {
				'id': art['id'],
				'title': art['title'],
				'icon': icon,
			}

			articles.append(article)

		topics = []
		fields = {'id':1, 'long':1, 'title':1, 'src_name':1, 'icons':1, 'pubtime':1}

		longs = set()
		for topic in tids:
			for id in topic['ids']:
				longs.add(id['article'])

		longs = list(longs)
		xarts = find_articles('long', longs, fields=fields)
		xarts = dict((x['long'], x) for x in xarts)
		for topic in tids:
			arts, last = [], 0
			for id in topic['ids']:
				if id['article'] not in xarts:
					continue

				art = xarts[id['article']]

				val = random.choice(art['icons'].values()) if art['icons'] else None
				icon = icon2url(val, 220, 120) if val is not None else ''

				article = {
					'id': art['id'],
					'title': art['title'],
					'src_name': art['src_name'],
					'icon': icon,
					'pubdate': time2best(art['pubtime']),
				}

				arts.append(article)
				last = id['article']

			topics.append({'cate':topic['cate'], 'articles':arts, 'last':last})

		return dict(articles=articles, topics=topics)


class Latest(Resource):

	def get(self):
		last = request.args.get('last')
		limit = request.args.get('limit', 20, int)
		res = self.common(last, limit)
		
		if request.args.get('hots') == 'true':
			res['hots'] = get_hots(random.randint(0, 50))
			res['keywords'] = get_keywords(random.randint(0, 50))

		return res

	@cache.memoize(timeout=60)
	def common(self, last, limit=20):
		if limit > 20 or limit < 1:
			limit = 20

		ids = self.latest()

		articles = []
		offset = 0

		if last is not None:
			for index, id in enumerate(ids):
				if id == last:
					offset = index + 1
					break

		last = 0
		ids = ids[offset:offset + limit]

		fields = {'id':1, 'title':1, 'src_name':1, 'icons':1, 'pubtime':1}
		arts = find_articles('id', ids, fields=fields)
		arts = dict((x['id'], x) for x in arts)
		for id in ids:
			if id not in arts:
				continue

			art = arts[id]

			val = random.choice(art['icons'].values()) if art['icons'] else None
			icon = icon2url(val, 220, 120) if val is not None else ''

			articles.append({
				'id': art['id'],
				'title': art['title'],
				'src_name': art['src_name'],
				'icon': icon,
				'icons': [icon2url(x, 220, 120) for x in art['icons'].itervalues()],
				'icon_cnt': len(art['icons']),
				'pubdate': time2best(art['pubtime']),
			})
			last = id

		if len(ids) < limit:
			last = 0

		return dict(articles=articles, last=last)

	@cache.cached(timeout=30)
	def latest(self):
		ids = mongo.article.find({'sim':True}, {'id':1}).sort([('pubtime', -1)]).limit(400)
		return [x['id'] for x in ids]


class Cates(Resource):

	def get(self):
		res = []
		for cate in cates:
			tags, xmax = [], len(topics[cate])
			while True:
				tag = random.choice(topics[cate])
				if tag in tags:
					continue
				tags.append(tag)
				if len(tags) == 12 or len(tags) == xmax:
					break
			tags = tags2icon(tags)
			res.append(dict(cate=cate, tags=tags))
		return dict(cates=res)


class Topic(Resource):

	def get(self, word):
		last = request.args.get('last', None, long)
		limit = request.args.get('limit', 20, int)
		res = self.common(word, last, limit)

		if request.args.get('hots') == 'true':
			res['hots'] = get_hots(random.randint(0, 50))
			res['keywords'] = get_keywords(random.randint(0, 50))

		return res

	@cache.memoize(timeout=60)
	def common(self, word, last, limit=20):
		articles = []
		if limit > 20 or limit < 1:
			limit = 20

		count, topic = find_topic(word, last=last, limit=limit)
		if topic is None:
			return dict(word=word, articles=articles, last='')

		fields = {'id':1, 'long':1, 'title':1, 'src_name':1, 'icons':1, 'pubtime':1}
		longs = [x['article'] for x in topic]
		arts = find_articles('long', longs, fields=fields)
		arts = dict((x['long'], x) for x in arts)
		for id in topic:
			if id['article'] not in arts:
				remove_index({'article':id['article']})
				current_app.logger.error('article not found: %d' % id['article'])
				continue
			
			art = arts[id['article']]

			val = random.choice(art['icons'].values()) if art['icons'] else None
			icon = icon2url(val, 220, 120) if val is not None else ''

			articles.append({
				'id': art['id'],
				'title': art['title'],
				'src_name': art['src_name'],
				'icon': icon,
				'icons': [icon2url(x, 220, 120) for x in art['icons'].itervalues()],
				'icon_cnt': len(art['icons']),
				'pubdate': time2best(art['pubtime']),
			})
			last = id['article']

		return dict(word=word, articles=articles, last=last, count=count)


class TopicPage(Resource):

	def get(self, word, page):
		limit = request.args.get('limit', 20, int)
		res = self.common(word, page, limit)

		res['hots'] = get_hots(random.randint(0, 50))
		res['keywords'] = get_keywords(random.randint(0, 50))

		return res

	@cache.memoize(timeout=60)
	def common(self, word, page, limit=20):
		articles = []
		if limit > 20 or limit < 1:
			limit = 20

		page = max(1, min(page, 100))

		count, topic = find_topic_page(word, page)
		if topic is None:
			return dict(word=word, articles=articles, last='')

		fields = {'id':1, 'long':1, 'title':1, 'src_name':1, 'icons':1, 'pubtime':1}
		longs = [x['article'] for x in topic]
		arts = find_articles('long', longs, fields=fields)
		arts = dict((x['long'], x) for x in arts)
		for id in topic:
			if id['article'] not in arts:
				remove_index({'article':id['article']})
				current_app.logger.error('article not found: %d' % id['article'])
				continue
			
			art = arts[id['article']]

			val = random.choice(art['icons'].values()) if art['icons'] else None
			icon = icon2url(val, 220, 120) if val is not None else ''

			articles.append({
				'id': art['id'],
				'title': art['title'],
				'src_name': art['src_name'],
				'icon': icon,
				'icons': [icon2url(x, 220, 120) for x in art['icons'].itervalues()],
				'icon_cnt': len(art['icons']),
				'pubdate': time2best(art['pubtime']),
			})

		return dict(word=word, articles=articles, count=count)


api.add_resource(Index, '/index')
api.add_resource(Latest, '/latest')
api.add_resource(Cates, '/cates')
api.add_resource(Topic, '/topics/<string:word>/')
api.add_resource(TopicPage, '/topics/<string:word>/<int:page>')