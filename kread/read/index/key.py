# coding: utf-8
import re
import math
import hashlib
from collections import OrderedDict
from utils import unicode2hash

__all__ = [
	'Keyword',
]


RE_FILTER = re.compile(ur'www\.|\.com|\.cn|\.org|http|记者|报道|北京时间|[:,?。：，？]')


class Keyword(object):

	def __init__(self, redis_word):
		self.redis = redis_word
		self.update()

	def update(self):
		total = self.redis.get('total')
		total = int(total) if total is not None else 0
		self.total = float(max(1, total))

	def word2num(self, word):
		word = word.lower()
		hkey = unicode2hash(word)
		key = hkey % 500
		num = self.redis.hget(key, hkey)
		num = int(num) if num is not None else 0
		return float(max(1, num))

	def dfs(self, title, words):
		tfs_filter = (lambda x: (2 <= len(x[0]) <= 7 \
				or x[0] in words['eng'] and 2 <= len(x[0]) <= 20) and not RE_FILTER.match(x[0])) 
		tfs = dict(filter(tfs_filter, words['all'].iteritems()))
		if len(tfs) < 10:
			return None

		tfs_sum = float(sum(tfs.itervalues()))
		dfs = {}
		for word, tf in tfs.iteritems():
			af = self.word2num(word)
			bf = (min(10, af) + min(af, 50) * 0.2 + min(af, 100) * 0.1) ** 2.5
			cf = math.log(max(1.00001, self.total / af)) ** 1.5
			lf = min(len(word), 4) ** 2
			df = lf * tf / tfs_sum * cf * bf
			if word in title:
				df *= 10
			elif word not in words['src']:
				df *= 5
			dfs[word] = df
		return dfs

	def efs(self, title, words, dfs):
		xdfs = OrderedDict(sorted(dfs.iteritems(), key=lambda x: -x[1]))
		dfs = {}
		for word, df in xdfs.items():
			if word not in title:
				dfs[word] = xdfs.pop(word)

		efs, word = {}, None
		while xdfs:
			if word is None:
				word, df = xdfs.popitem()
			off = title.index(word)
			for word2, df2 in xdfs.items():
				off2 = title.index(word2)
				wlen, wlen2 = len(word), len(word2)
				if wlen + wlen2 <= 8 and (wlen <= 3 and wlen2 <= 3) \
						or word in words['eng'] and wlen2 <= 3 \
						or word2 in words['eng'] and wlen <= 3 \
						or word in words['eng'] \
							and word2 in words['eng'] \
							and wlen + wlen2 <= 30:
					xor = int(word in words['nr']) ^ int(word2 in words['nr'])
					if off + wlen == off2 and not xor \
							and (word not in words['nr'] or wlen <= 2) \
							and (word2 not in words['nr'] or wlen2 <= 2):
						efs[word] = df
						efs[word2] = xdfs.pop(word2)
						word, df = word + word2, df + df2
						break
					elif off == off2 + wlen2 and not xor \
							and (word not in words['nr'] or wlen <= 2) \
							and (word2 not in words['nr'] or wlen2 <= 2):
						efs[word] = df
						efs[word2] = xdfs.pop(word2)
						word, df = word2 + word, df + df2
						break
				if off + wlen == off2 - 1 and title[off2 - 1] == u'·':
					efs[word] = df
					efs[word2] = xdfs.pop(word2)
					word, df = word + u'·' + word2, df + df2
					break
				if off - 1 == off2 + wlen2 and title[off - 1] == u'·':
					efs[word] = df
					efs[word2] = xdfs.pop(word2)
					word, df = word2 + u'·' + word, df + df2
					break
			else:
				dfs[word] = df
				word = None
				continue

			if word in xdfs:
				df += xdfs.pop(word)

		xdfs, dfs, word = dfs, {}, None
		while xdfs:
			if word is None:
				word, df = xdfs.popitem()
			for word2, df2 in xdfs.items():
				if word in word2:
					xdfs.pop(word2)
					if df / df2 < 20:
						efs[word] = df
						word, df = word2, df + df2
						break
					else:
						efs[word2] = df2
						df += df2
				elif word2 in word:
					xdfs.pop(word2)
					if df2 / df >= 20:
						efs[word] = df
						word, df = word2, df + df2
						break
					else:
						efs[word2] = df2
						df = df + df2
			else:
				dfs[word] = df
				word = None

		for word in efs.keys():
			if word in dfs:
				efs.pop(word)

		num = min(dfs.itervalues())
		for word in dfs:
			dfs[word] = max(1, (dfs[word] / num) ** 0.15)
		for word in efs:
			efs[word] = max(1, (efs[word] / num) ** 0.15)

		tmp = dfs.copy()
		tmp.update(efs)

		def score(word):
			word = word.lower()
			hkey = unicode2hash(word)
			key = hkey % 500
			df = self.redis.hget(key, hkey)
			df = int(df) if df is not None else 0
			return df >= 5

		tmp = filter(lambda x: score(x[0]), tmp.iteritems())
		tmp = sorted(tmp, key=lambda x: -x[1])
		keys = [x for x, _ in tmp[:3]]
		index = dict(tmp[:10])

		return keys, index, dfs, efs

	def make(self, title, words):
		dfs = self.dfs(title, words)
		if dfs is None:
			return None

		keys, index, dfs, efs = self.efs(title, words, dfs)
		return {'keys':keys, 'index':index}
