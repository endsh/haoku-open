# coding: utf-8
import re
import time
import tldextract
import unittest
import urlparse
from urllib import unquote
from .char import t, u

RE_GOOD_VALUE = re.compile('^[\w\-]*$')
RE_DATE = re.compile('[\/\-_](20\d{2})[\/\-_]?(0\d|1[0-2])[\/\-_]?(0[1-9]|[12]\d|3[01])?[\/\-_]')


def url2filetype(abs_url):
	""" return the filetype of the file specified by the url. """
	path = urlparse.urlparse(abs_url).path
	if path.endswith('/'):
		path = path[:-1]
	path_chunks = [x for x in path.split('/') if len(x) > 0]
	last_chunk = path_chunks[-1].split('.') if path_chunks else []
	file_type = last_chunk[-1] if len(last_chunk) >= 2 else None
	return file_type or None


def url2tpl(abs_url):
	""" return the template of url """
	tpl, count = abs_url, 1
	while count > 0:
		tpl, count = re.subn(ur'([\/\-_a-zA-Z=])(\d+)([\/\-_.]|$)', '\g<1><d>\g<3>', tpl)
	return tpl
	res = urlparse.urlparse(abs_url)
	return res.netloc + re.sub('\d+', '<d>', res.path)


def url2time(abs_url):
	""" return time of article """
	now = time.time()
	match = RE_DATE.search(abs_url)
	if match:
		year, month, day = match.group(1), match.group(2), match.group(3)

		if not day:
			day = '01'

		try:
			return min(now, time.mktime(time.strptime(
				'%s-%s-%s' % (year, month, day), "%Y-%m-%d")) + 43200)
		except:
			pass

	return time.time() - (86400 * 30)


def trim_url(abs_url):
	return url.split('#')[0].split('?')[0]


def get_host(abs_url, **kwargs):
	""" returns a url's host. """
	if abs_url is None:
		return None
	return urlparse.urlparse(abs_url, **kwargs).netloc


def get_domain(abs_url, **kwargs):
	""" returns a url's host. """
	if abs_url is None:
		return None
	ext = tldextract.extract(abs_url, **kwargs)
	return '%s.%s' % (ext.domain, ext.suffix)


def get_subdomains(abs_url, **kwargs):
	""" returns a url's host. """
	if abs_url is None:
		return None
	return list(reversed(tldextract.extract(abs_url, **kwargs).subdomain.split('.')))

def get_scheme(abs_url, **kwargs):
	""" returns a url's scheme. """
	if abs_url is None:
		return None
	return urlparse.urlparse(abs_url, **kwargs).scheme


def get_path(abs_url, **kwargs):
	""" returns a url's path. """
	if abs_url is None:
		return None
	return urlparse.urlparse(abs_url, **kwargs).path


def resolve_url(abs_url, **kwargs):
	if abs_url is None:
		return None

	res = urlparse.urlparse(abs_url, **kwargs)
	url = '%s://%s%s' % (res.scheme, res.netloc, res.path)
	if res.query and '.htm' not in url:
		params = {}
		for key, value in urlparse.parse_qs(res.query).iteritems():
			if RE_GOOD_VALUE.match(value[0]):
				params[key] = value[0]
		if params:
			url += '?%s' % '&'.join(['%s=%s' % (k, v) for k, v in params.iteritems()])
	return url[:-1] if url and url[-1] == '/' else url


def is_abs_url(url):
	""" this regex was brought to you by django! """
	regex = re.compile(
		r'^(?:http|ftp)s?://' # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
		r'localhost|' # localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
		r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)

	c_regex = re.compile(regex)
	return (c_regex.search(url) != None)


def get_index(url):
	return 'http://www.%s' % get_domain(url)


def get_sub_index(url):
	return 'http://%s' % get_host(url)


def url2score(url):
	score = 0
	subdomains = list(reversed(tldextract.extract(url).subdomain.split('.')))
	if len(subdomains) == 1:
		if subdomains[0] != 'www':
			score += 0.1
	elif len(subdomains) > 1:
		score += len(subdomains) * 2 - 1

	res = urlparse.urlparse(url)
	paths = res.path.split('/')
	if len(paths) > 0:
		if not paths[0]:
			paths = paths[1:]
	if len(paths) > 0:
		if not paths[-1]:
			paths = paths[:-1]

	for path in paths:
		if re.match('^<d>$', path):
			score += 0.2
		elif re.match('^<d>.(html|htm|shtm|shtml)$', path):
			score += 0.2
		elif len(path) == 1:
			score += 0.2
		else:
			score += 0.6

	words = 'news|ent|sports|auto|tech|digi|mobile|lady|edu|war|mil|fashion'.split('|')
	subs = get_subdomains(url)
	for w in words:
		if w in words:
			score -= 0.5
			break

	# if len(paths) == 1 and not paths[0]:
	# 	score -= 1

	params = urlparse.parse_qs(res.query)
	for k, v in params.iteritems():
		if re.match('^<d>$', v[0]):
			score += 0.3
		else:
			score += 0.5

	return 1 + score


class UrlsTest(unittest.TestCase):

	def test_url2filetype(self):
		self.assertEqual(url2filetype('http://www.baidu.com/index.html'), 'html')
		self.assertEqual(url2filetype('http://music.baidu.com/test.mp3'), 'mp3')
		self.assertEqual(url2filetype('http://www.baidu.com/static/hello.jpg'), 'jpg')
		self.assertEqual(url2filetype('http://www.baidu.com/index.php?k='), 'php')
		self.assertEqual(url2filetype('http://www.baidu.com/index.asp?k='), 'asp')
		self.assertEqual(url2filetype('http://www.yidianzixun.com/#type=article&id='), None)

	def test_get_domain(self):
		self.assertEqual(get_domain('http://news.qq.com/a/20140729/023633.htm'), 'news.qq.com')
		self.assertEqual(get_domain('http://www.36kr.com/p/213278.html'), 'www.36kr.com')
		self.assertEqual(get_domain('http://news.sohu.com/20140724/n402653919.shtml'), 'news.sohu.com')
		self.assertEqual(get_domain('http://ent.ifeng.com/a/20140728/40205648_0.shtml'), 'ent.ifeng.com')
		self.assertEqual(get_domain('http://www.yidianzixun.com/#type=article&id='), 'www.yidianzixun.com')

	def test_get_scheme(self):
		self.assertEqual(get_scheme('http://news.qq.com/'), 'http')
		self.assertEqual(get_scheme('ftp://news.qq.com/'), 'ftp')
		self.assertEqual(get_scheme('https://news.qq.com/'), 'https')
		self.assertEqual(get_scheme('news.qq.com'), '')

	def test_get_path(self):
		self.assertEqual(
			get_path('http://news.qq.com/a/20140729/023633.htm'), 
			'/a/20140729/023633.htm')
		self.assertEqual(
			get_path('http://www.36kr.com/p/213278.html'), 
			'/p/213278.html')
		self.assertEqual(
			get_path('http://news.sohu.com/20140724/n402653919.shtml'), 
			'/20140724/n402653919.shtml')

	def test_is_abs_url(self):
		self.assertEqual(is_abs_url('news.qq.com'), False)
		self.assertEqual(is_abs_url('ftp://news.qq.com/'), True)
		self.assertEqual(is_abs_url('https://news.qq.com/abc'), True)
		self.assertEqual(is_abs_url('haoku://www.haoku.net/index.html'), False)
		self.assertEqual(is_abs_url('/index.html'), False)


if __name__ == '__main__':
	unittest.main()