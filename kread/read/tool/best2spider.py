# coding: utf-8
import redis
import urlparse
import pymongo
import hashlib
import conf
from db import MongoBest, MongoSpider, MongoIWeb
from utils import get_domain, get_subdomains, get_path
from utils import recreate_local_cache
from utils import load_json, save_json

redis_word = redis.Redis(**conf.redis_word)
redis_tag = redis.Redis(**conf.redis_tag)
redis_time = redis.Redis(**conf.redis_time)
redis_url = redis.Redis(**conf.redis_url)


class URLTree(object):

	def __init__(self):
		self.root = {}

	def add(self, cate):
		url = cate['url']

		domain = get_domain(url)
		subdomains = get_subdomains(url)
		paths = get_path(url).split('/')
		query = urlparse.urlparse(url).query

		if domain not in self.root:
			self.root[domain] = {'sub':{}, 'path':{}}

		node = self.root[domain]
		if len(subdomains) > 1 or len(subdomains) == 1 and subdomains[0] != 'www':
			for sub in subdomains:
				if sub not in node['sub']:
					node['sub'][sub] = {'sub':{}, 'path':{}}
				node = node['sub'][sub]

		for path in paths:
			if path not in node['path']:
				node['path'][path] = {'path':{}}
			node = node['path'][path]

		if query:
			node['path']['query___' + query] = {'path':{}}
			node = node['path']['query___' + query]

		node['cate'] = cate

	def refresh(self):
		for node in self.root.itervalues():
			self.refresh_node(node)

	def refresh_node(self, node, name=''):
		if 'cate' in node:
			if node['cate']['name'].strip():
				name = node['cate']['name'].strip()
			node['cate']['name'] = name
		elif 'sub' in node and node['sub'] and '' in node['path'] and 'cate' in node['path']['']:
			if node['path']['']['cate']['name'].strip():
				name = node['path']['']['cate']['name'].strip()

		if 'sub' in node:
			for sub in node['sub'].itervalues():
				self.refresh_node(sub, name)

		for path in node['path'].itervalues():
			self.refresh_node(path, name)


def make_mongo():
	best = MongoBest(conf.mongo_web)
	cates = {}
	tpls = {}
	domains = {}
	tree = URLTree()

	for cate in best.catecory.find():
		obj = {}
		obj['_id'] = hashlib.md5(cate['_id'].encode('utf-8')).hexdigest()
		obj['url'] = cate['_id']
		obj['name'] = cate['name']
		obj['tags'] = filter(lambda x: x, cate['tag'].split('|'))
		obj['cate'] = cate['cate']
		obj['domain'] = get_domain(obj['url'])
		obj['page'] = ''
		obj['all'] = False
		obj['arts'] = 0
		obj['index'] = -1
		obj['log'] = []
		obj['fetch'] = 0
		obj['null'] = 0
		obj['error'] = 0
		obj['status'] = 'common'
		obj['next'] = 0
		obj['last'] = 0
		cates[obj['_id']] = obj

		tree.add(obj)

		if obj['domain'] not in domains:
			domains[obj['domain']] = {
				'_id':obj['domain'], 
				'name':'',
				'link': 'http://www.%s/' % obj['domain'],
				'cates':0,
				'tpls':0,
				'arts':0,
				'articles':0,
				'status':'common',
				'last':0,
			}

		subdomains = get_subdomains(obj['url'])
		if len(subdomains) == 1 and subdomains[0] in ['www', ''] \
				and get_path(obj['url']) in ['', '/']:
			domains[obj['domain']]['name'] = obj['name']
		domains[obj['domain']]['cates'] += 1

	tree.refresh()

	# for cate in cates.itervalues():
	# 	print '%-120s %s' % (cate['_id'], cate['name'])

	for tpl in best.template.find():
		tpl['domain'] = get_domain(tpl['_id'])
		tpl['arts'] = 0
		tpl['articles'] = 0
		tpl['status'] = 'common'
		tpl['last'] = 0
		if tpl['domain'] not in domains:
			print 'tpl(%s) not in domain(%s)' % (tpl['_id'], tpl['domain'])
			continue
		tpls[tpl['_id']] = tpl
		domains[tpl['domain']]['tpls'] += 1

	save_json('spider/domains.json', domains)
	save_json('spider/cates.json', cates)
	save_json('spider/tpls.json', tpls)


def update_mongo():
	domains = load_json('spider/domains.json')
	cates = load_json('spider/cates.json')
	tpls = load_json('spider/tpls.json')

	iweb = MongoIWeb(conf.mongo_iweb)

	iweb.index.drop()
	iweb.topic.drop()
	iweb.article.drop()
	iweb.spider_article.drop()
	iweb.spider_exc.drop()
	iweb.sim.drop()
	iweb.catecory.drop()
	iweb.template.drop()
	iweb.domain.drop()
	iweb.image.drop()

	redis_tag.flushdb()
	redis_time.flushdb()
	redis_url.flushdb()

	iweb.index.create_index()
	iweb.topic.create_index()

	iweb.article.create_index([('id', pymongo.ASCENDING)])
	iweb.article.create_index([('long', pymongo.ASCENDING)])
	iweb.article.create_index([('pubtime', pymongo.DESCENDING)])
	iweb.sim.create_index()

	index = [
		[
			('id', pymongo.ASCENDING),
		],
		[
			('long', pymongo.ASCENDING),
		],
		[
			('f', pymongo.DESCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('domain', pymongo.ASCENDING),
			('f', pymongo.ASCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('v.seg', pymongo.DESCENDING),
		],
		[
			('version', pymongo.DESCENDING),
		],
		[
			('pubtime', pymongo.DESCENDING),
		]
	]

	for i in index:
		iweb.spider_article.create_index(i)

	index = [
		[
			('id', pymongo.ASCENDING),
		],
		[
			('long', pymongo.ASCENDING),
		],
		[
			('f', pymongo.DESCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('domain', pymongo.ASCENDING),
			('f', pymongo.ASCENDING),
			('pubtime', pymongo.DESCENDING),
		],
		[
			('pubtime', pymongo.DESCENDING),
		]
	]

	for i in index:
		iweb.spider_exc.create_index(i)

	iweb.catecory.create_index([
		('domain', pymongo.ASCENDING),
		('status', pymongo.ASCENDING),
		('next', pymongo.ASCENDING),
	])

	iweb.template.create_index([
		('domain', pymongo.ASCENDING),
		('status', pymongo.ASCENDING),
	])


	iweb.domain.create_index('status', pymongo.ASCENDING)

	for _id, domain in domains.iteritems():
		print _id, domain['name'], domain['cates'], domain['tpls']
		iweb.domain.save(domain)

	for cate in cates.itervalues():
		iweb.catecory.save(cate)

	for tpl in tpls.itervalues():
		iweb.template.save(tpl)

	print len(domains)


def drop_cache():
	if conf.RELEASE:
		return
	recreate_local_cache('scheduler/html')
	recreate_local_cache('scheduler/image')
	recreate_local_cache('scheduler/text')
	recreate_local_cache('scheduler/word')


def main():
	redis.Redis(**conf.redis_word).flushdb()
	redis.Redis(**conf.redis_url).flushdb()
	redis.Redis(**conf.redis_tag).flushdb()
	redis.Redis(**conf.redis_cluster).flushdb()
	redis.Redis(**conf.redis_topic).flushdb()
	drop_cache()
	if not conf.RELEASE:
		make_mongo()
	update_mongo()


if __name__ == '__main__':
	main()