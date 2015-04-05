# coding: utf-8
from utils import get_time, url2time
from .base import BaseParser, REGEXES

__all__ = [
	'TimeParser',
]


class TimeParser(BaseParser):

	def parse(self):
		res = {'int':0, 'str':''}
		pubtime = self.parse_time()
		if not pubtime:
			return res

		res['str'] = pubtime
		timestamp = get_time(pubtime)
		if pubtime < 946656000:
			pubtime = url2time(self.article.url)
			res['int'] = pubtime
		else:
			res['int'] = url2time(self.article.url)
		return res

	def parse_time(self):
		dates = REGEXES['time'].findall(self.article.html)
		if not dates:
			return ''

		for _,year,_,_,month,_,date,_,hour,minute,_,second in dates:
			if minute:
				date = '%4d-%02d-%02d %02d:%02d' % (
					int(year), int(month), int(date), int(hour), int(minute))
				if second:
					date = '%s:%02d' % (date, int(second))
				return date

		return '%4d-%02d-%02d' % (
					int(dates[0][1]), int(dates[0][4]), int(dates[0][6]))