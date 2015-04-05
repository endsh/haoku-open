# coding: utf-8
import re
import time
from utils import PQDict, html2urls, url2tpl
from spider.cmd import handle


class Catecorys(object):

	def __init__(self, domain):
		self.domain = domain
		self.domains = domain.domains
		self.mongo = self.domains.catecory
		self.log = domain.log
		self.waiting = PQDict(
			key=lambda x: x.value['_id'],
			score=lambda x: x.value['next'],
		)
		self.doing = dict()
		self.updates = set()
		self.next = 0
		self.null = False
		self.wait = 0

	def __nonzero__(self):
		return len(self.waiting) > 0

	def __len__(self):
		return len(self.waiting)

	def put(self, cate, update=False):
		self.waiting.put(cate)
		if cate['next'] < self.wait:
			self.wait = cate['next']
		if update:
			self.updates.add(cate['_id'])

	def save(self, cate, update=False):
		if update == True or cate['_id'] in self.updates:
			if cate['_id'] in self.updates:
				self.updates.remove(cate['_id'])
			self.mongo.save(cate)
			return 1
		return 0

	def sync(self, exit):
		if exit:
			self.back_on_exit()
		else:
			if time.time() >= self.next or self.next == 0:
				next = time.time() + 3600
				self.back(next)
				self.load(next)
				self.next = next

	def load(self, next):
		doc = {
			'domain': self.domain.id(),
			'status': 'common',
			'$or': [{'next': {'$gte': self.next, '$lt':next}}, {'last':0}],
		}
		cates = self.mongo.find(doc)
		for cate in cates:
			if cate['_id'] not in self.waiting \
					and cate['_id'] not in self.doing:
				self.put(cate)

		if cates.count() > 0:
			self.log.info('load %d/%d cates from %s.'
				% (cates.count(), len(self.waiting), self.domain.id()))

	def back(self, next):
		num, others = 0, []
		for cate in self.waiting.itervalues():
			if cate['next'] >= next:
				num += self.save(cate)
			else:
				others.append(cate)
		self.waiting.extend(others)
		if num > 0:
			self.log.info('back %d/%d cate from %s.'
				% (num, len(others), self.domain.id()))

	def back_on_exit(self):
		num, count = 0, len(self.waiting)
		for cate in self.waiting.itervalues():
			num += self.save(cate)
		self.log.info('back %d/%d cates from %s on exit.'
			% (num, count, self.domain.id()))

	def get(self, now):
		if self.wait <= now and self.waiting:
			cate = self.waiting.get()
			self.wait = cate['next']
			if self.wait <= now:
				self.doing[cate['_id']] = cate

				if self.waiting:
					with self.waiting.get2do() as tmp:
						self.wait = tmp['next']
				else:
					self.wait = 2000000000

				if not cate['page']:
					return {'_id':cate['_id'], 'domain':cate['domain'], 'url':cate['url']}
				else:
					return {'_id':cate['_id'], 'domain':cate['domain'], 'url':cate['page']}
			self.waiting.put(cate)

	def cancel(self, page):
		if page['_id'] not in self.doing:
			return
		cate = self.doing[page['_id']]
		self.waiting.put(cate)
		if cate['next'] < self.wait:
			self.wait = cate['next']

	def fetch(self, page, res):
		if page['_id'] not in self.doing:
			return

		cate = self.doing[page['_id']]
		cate['fetch'] += 1
		cate['last'] = time.time()
		self.updates.add(cate['_id'])
		if 'exc' not in res:
			self.domains.new_handle(cate['_id'], ('cate', page, {'html':res['html']}))
			self.log.debug('fetch cate: %s.' % cate['url'])
		else:
			log = {'last':time.time(), 'url':page['url'], 'exc':res['exc'], 'arts':0}
			self.make_log(cate, log)
			cate['next'] = self.get_next(cate)
			cate['error'] += 1
			cate = self.doing.pop(page['_id'])
			self.put(cate, update=True)
			self.log.warn('fetch cate except(%s): %s.'
				% (res['exc'], page['url']))

	def handle(self, page, res):
		if page['_id'] not in self.doing:
			return

		log = {'last':time.time(), 'url':page['url'], 'exc':'', 'arts':0}
		cate = self.doing.pop(page['_id'])
		if 'exc' not in res:
			count = self.domain.new_arts(res['urls'], 'cate', cate, last=cate['next'] - 900)
			if count == 0:
				cate['null'] += 1
			else:
				cate['arts'] += count
				log['arts'] = count

			if not cate['all'] or count > 0:
				if res['next']:
					cate['page'] = res['next']
				else:
					cate['page'] = ''
					cate['all'] = True
			else:
				cate['page'] = ''

			self.log.debug('parse %d arts from cate: %s.'
				% (count, page['url']))
		else:
			log['exc'] = res['exc']
			cate['error'] += 1
			if cate['error'] >= 20:
				cate['all'] = True
			self.log.warn('parse except %s from cate: %s.'
				% (res['exc'], page['url']))

		self.make_log(cate, log)
		cate['next'] = self.get_next(cate)
		cate['last'] = time.time()
		self.put(cate, update=True)

	def make_log(self, cate, log):
		cate['index'] += 1
		if cate['index'] >= 10:
			cate['index'] = 0

		if len(cate['log']) < 10:
			cate['log'].append(log)
		else:
			cate['log'][cate['index']] = log

	def get_next(self, cate):
		if not cate['all']:
			return time.time() + 60
			
		if cate['log']:
			arts = sum([x['arts'] for x in cate['log']])
			error = sum([1 if x['exc'] != '' else 0 for x in cate['log']])
			null = sum([1 if x['arts'] == 0 \
				and x['exc'] == 0 else 0 for x in cate['log']])
			start = min(cate['log'], key=lambda x: x['last'])['last']
			end = max(cate['log'], key=lambda x: x['last'])['last']
			if error == 10:
				return time.time() + 300
			return time.time() + 60 + (end - start) / float(arts + 5) \
				+ null * 10 + error * 60
		return time.time() + 120


def get_pages(urls):
	pages = []
	tpl = ''
	for url, texts in urls.iteritems():
		for text in texts:
			if re.match(ur'^(prev|next|第\d+页|上.*页|下.*页|未页|尾页|最后一页)$', text, re.I):
				if 'next' in url:
					continue
				pages.append(url)
				tpl = url2tpl(url)
				break
			match = re.match('^\d+$', text)
			if match:
				num = match.group(0)
				for item in re.findall('\d+', url):
					if item == num:
						pages.append(url)
						break

	pages = filter(lambda x: url2tpl(x) == tpl, pages)

	return pages


def cmp_nums(nums, other):
	for i, num in enumerate(nums):
		if len(other) <= i:
			return 1
		if other[i] < num:
			return 1
		elif other[i] > num:
			return -1
	return 0


def get_next(page, urls):
	pages = get_pages(urls)
	if not pages:
		return ''

	res = {}
	for url in pages:
		res[url] = map(lambda x: int(x), re.findall('\d+', url))

	res = sorted(res.iteritems(), cmp=cmp_nums)
	if url2tpl(page) != url2tpl(pages[0]):
		return res[0][0]
	
	nums = map(lambda x: int(x), re.findall('\d+', page))
	for url, other in res:
		if cmp_nums(nums, other) < 0:
			return url

	return ''


@handle('cate')
def get_urls(handler, key, page, ext):
	urls = html2urls(ext['html'], page['url'])
	next = get_next(page['url'], urls)
	return {'urls':urls.keys(), 'next':next}
