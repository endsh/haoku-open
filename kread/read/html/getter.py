# coding: utf-8
from __future__ import unicode_literals
import sys
from Queue import Queue
from utils.worker import GroupWorker
from utils import get_domain, get_path, get_subdomains
from utils import get, get_or_cache, clean_html
from utils import tag2text, html2urls, print_dict
from collections import defaultdict

cates = '新闻|科技|数码|娱乐|体育|军事|教育|财经|旅游|文化|历史|健康|美食|时尚|星座|女性|育儿|汽车|房产|家居|公益|佛学|游戏|摄影|图片|博客|城市'.split('|')
provinces = u'北京|天津|上海|重庆|河北|河南|云南|辽宁|湖南|安徽|山东|新疆|江苏|浙江|江西|湖北|广西|甘肃|山西|内蒙古|陕西|吉林|福建|贵州|广东|青海|西藏|四川|宁夏|海南|台湾|香港|澳门'.split('|')

urls = [
	# 'http://www.qq.com/',
	# 'http://www.yixieshi.com/',
	# 'http://www.sina.com.cn/',
	# 'http://www.xinhuanet.com/',
	# 'http://www.people.com.cn/',
	'http://www.hexun.com/',
	'http://www.huanqiu.com/',
	'http://www.chinanews.com/',
	'http://www.china.com.cn/',
	'http://www.81.cn/',
	'http://www.36kr.com/',
	'http://www.huxiu.com/',
	'http://www.techweb.com.cn/',
	'http://www.tech2ipo.com/',
	'http://www.163.com/',
	'http://www.sohu.com/',
	'http://www.iheima.com/',
	'http://www.tmtpost.com/',
	'http://www.ifanr.com/',
	'http://www.ithome.com/',
	'http://www.ittime.com.cn/',
	'http://www.cnblogs.com/',
	'http://www.iresearch.com/',
	'http://www.cnbeta.com/',
	'http://www.ikancai.com/',
	'http://www.youth.cn/',
	'http://www.taiwan.cn/',
	'http://www.haiwainet.cn/',
	'http://www.ifeng.com/',
]


def url2meta(url, get=get):
	try:
		html = get(url)
	except ValueError:
		return None
	return html2meta(html, url)


def html2meta(html, url):
	doc = clean_html(html, url, return_doc=True)
	return doc2meta(doc, url)


def doc2meta(doc, url):
	keywords = tag2text(doc, 'meta', name='keywords')
	keywords = keywords.replace(u'，', ',')
	if ',' in keywords:
		keywords = [x.strip() for x in keywords.split(',')]
	elif '|' in keywords:
		keywords = [x.strip() for x in keywords.split('|')]
	elif '_' in keywords:
		keywords = [x.strip() for x in keywords.split('_')]
	elif '-' in keywords:
		keywords = [x.strip() for x in keywords.split('-')]
	elif keywords.count(' ') > 2:
		keywords = [x.strip() for x in keywords.split(' ')]
	else:
		keywords = [keywords]
	keywords = filter(lambda x: x, keywords)
	return {
		'title': tag2text(doc, 'title'),
		'keywords': keywords,
		'favicon': tag2text(doc, 'link', rel='shortcut icon'),
		'rss': tag2text(doc, 'link', type='application/rss+xml', bad='comment'),
	}


class Domain(object):

	def __init__(self, url):
		self.url = url
		self.domain = get_domain(url)
		self.name = None
		self.text = None

	def run(self):
		html = get_or_cache(self.url)
		doc = clean_html(html, self.url, return_doc=True)
		urls = html2urls(html, self.url, name=False)
		urls = sorted(urls, key=self.score)

		name = tag2text(doc, 'meta', property="og:site_name")
		if name:
			self.name = self.text = name
		else:
			cnt = 10
			while cnt <= 100:
				if self.get_name(urls[:cnt]):
					print self.domain, cnt
					break
				cnt += 10

		if self.name is not None:
			self.get_sub(urls)

	def get_sub(self, urls):
		print '%s: %s %s' % (self.domain, self.name, self.text)
		for url in urls:
			res = url2meta(url, get=get_or_cache)
			if res is not None:
				if '_' in res['title']:
					xwords = res['title'].split('_')
				elif '|' in res['title']:
					xwords = res['title'].split('|')
				elif '-' in res['title']:
					xwords = res['title'].split('-')
				else:
					continue
				print url,
				if len(xwords) > 5:
					print '++++++++++++++++++++++++++++++++++++++++++++++++++++> tolong'
					continue
				if u'游戏' in res['title'] and u'官方网站' in res['title']:
					print '++++++++++++++++++++++++++++++++++++++++++++++++++++> game'
					continue
				if res['title'].count(u'小说') > 2:
					print '++++++++++++++++++++++++++++++++++++++++++++++++++++> xiaoshuo'
					continue
				if self.name + u'视频' in res['title'] and ('video' in url or 'v.' in url):
					print '++++++++++++++++++++++++++++++++++++++++++++++++++++> video'
					continue
				if self.name + u'论坛' in res['title'] and ('/t-' in url or 'bbs.' in url):
					print '++++++++++++++++++++++++++++++++++++++++++++++++++++> thread'
					continue
				for word in xwords:
					word = word.strip()
					if word != self.name and word != self.text:
						if word in cates \
								or word[-2:] in cates \
								or word[:2] in cates and len(word) == 4 and word[-2:] == u'首页' \
								or word.startswith(self.name) \
								or word.endswith(u'频道') \
								or word.endswith(u'中心'):
							print '#%s#' % word, '-',
						else:
							print word, '-',
				print

	def score(self, url):
		subdomains = filter(lambda x: x != 'www', get_subdomains(url))
		num = len(subdomains)
		num += len(get_path(url).split('/')) - 1
		return num

	def get_name(self, urls):
		words = defaultdict(int)
		for url in urls:
			res = url2meta(url, get=get_or_cache)
			if res is not None:
				if '_' in res['title']:
					xwords = res['title'].split('_')
				elif '|' in res['title']:
					xwords = res['title'].split('|')
				elif '-' in res['title']:
					xwords = res['title'].split('-')
				else:
					continue
				for word in xwords:
					if word.strip():
						lower = word.lower()
						if lower.endswith('.com.cn'):
							word = word[:-6]
						elif lower.endswith('.com') or lower.endswith('.net'):
							word = word[:-4]
						words[word] += 1

		name = defaultdict(int)
		for word, cnt in words.iteritems():
			if word.endswith(u'频道'):
				word = word[:-2]
			if len(word) > 2 and word[-2:] in cates:
				name[word[:-2]] += 1
				if name[word[:-2]] >= 3:
					self.name = self.text = word[:-2]
					if word[:-2] + u'网' in words:
						self.text = word[:-2] + u'网'
					return True

		words = sorted(words.iteritems(), key=lambda x: -x[1])[:2]
		if len(words) >= 2:
			if words[0][1] > words[1][1] + 3 * len(urls) * 0.1:
				self.name = self.text = words[0][0]
				if self.name.endswith(u'网'):
					self.name = self.name[:-1]
				return True


class Getter(GroupWorker):

	def __init__(self, log, count=10, timeout=1, waitout=0.1):
		GroupWorker.__init__(self, log=log, count=count, 
			timeout=timeout, name='getter')
		self.waitout = waitout
		self.domains = Queue()
		for url in urls:
			domain = Domain(url)
			self.domains.put(domain)

	def handle(self):
		while not self.domains.empty():
			domain = self.domains.get()
			domain.run()
			self.wait(self.waitout)
	

def main():
	import logging

	if len(sys.argv) >= 2:
		level = logging.DEBUG
	else:
		level = logging.INFO

	log = logging.getLogger(__name__)
	log.setLevel(level)
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
	_handler = logging.StreamHandler()
	_handler.setLevel(level)
	_handler.setFormatter(formatter)
	log.addHandler(_handler)

	getter = Getter(log)
	getter.forever()


if __name__ == '__main__':
	main()