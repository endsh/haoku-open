# coding: utf-8
import datetime
import time
import feedparser

beststr = sorted({
	120: u'刚刚',
	180: u'1分钟前',
	240: u'2分钟前',
	300: u'3分钟前',
	600: u'5分钟前',
	1800: u'10分钟前',
	3600: u'30分钟前',
	7200: u'1小时前',
	10800: u'2小时前',
	21600: u'3小时前',
	43200: u'6小时前',
	86400: u'12小时前',
}.iteritems())


def time2best(pubtime):
	if pubtime is None:
		return ''
		
	now = max(time.time(), pubtime) + 8 * 3600
	pub = pubtime
	pubtime += 8 * 3600
	if pubtime < (now - 86400) // 86400 * 86400:
		return time.strftime('%Y-%m-%d', time.localtime(pub))
	elif pubtime < now // 86400 * 86400:
		return u'昨天'
	
	offset = now - pubtime
	hours = offset // 3600
	if hours > 0:
		if hours >= 12:
			hours = 12
		elif hours > 6:
			hours = hours // 2 * 2
		return u'%s小时前' % int(hours)

	minutes = offset // 60
	if minutes > 1:
		if minutes >= 30:
			minutes = 30
		elif minutes >= 10:
			minutes = minutes // 10 * 10
		elif minutes >= 5:
			minutes = 5
		return u'%s分钟前' % int(minutes)

	return u'刚刚'


def get_time(unparsed_date):
	""" string to time """
	return time.mktime(get_datetime(unparsed_date).timetuple())


def get_datetime(unparsed_date):
	""" string to datetime """
	parsed_date = feedparser._parse_date(unparsed_date)
	if not parsed_date:
		return datetime.datetime.min
	if isinstance(parsed_date, dict):
		return datetime.datetime(
			parsed_date['year'],
			parsed_date['month'],
			parsed_date['day'],
			parsed_date['hour'],
			parsed_date['min'],
			parsed_date['sec'],
			tzinfo=None)
	else:
		return datetime.datetime(
			parsed_date[0],
			parsed_date[1],
			parsed_date[2],
			parsed_date[3],
			parsed_date[4],
			parsed_date[5],
			tzinfo=None)


def atime(info):
	""" time decorator """
	def wrapper(func):
		def new_func(*args, **kwargs):
			starttime = time.time()
			text = '[%s by %s() start at %lf]' % (info, func.__name__, starttime)
			text += '=' * (100 - len(text)) if len(text) < 100 else ''
			print text
			result = func(*args, **kwargs)
			endtime = time.time()
			text = '[%s by %s() end at %lf]' % (info, func.__name__, endtime)
			text += '-' * (100 - len(text)) if len(text) < 100 else ''
			print text
			print 'use time:', endtime - starttime
			return result
		new_func.__name__ = func.__name__
		return new_func
	return wrapper
