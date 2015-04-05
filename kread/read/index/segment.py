# coding: utf-8
import collections
import json
import re
import unittest
import jieba
import jieba.posseg as pseg
import pytrie
import utils

__all__ = [
	"segmentor",
]


name_flag = ['n','ng','nr','nrfg','nrt','ns','nt','nz', 'vn']
man_flag = ['nr', 'nrt', 'nrfg']
tuan_flag = ['nt']
space_flag = ['ns']
compos_flag = ['n', 'nr', 'nrfg','nrt', 'vn', 'ns', 'nz']
blackets = {
	'open':u'("（【“《',
	'close':u')"）】”》',
}

re_num = re.compile('[\d.]+')


class Segmentor(object):
	""" segment keyword """

	def __init__(self):
		""" init class """
		self.init = False

	def cut(self, text, words=None):
		""" cut text to word list """
		trie = pytrie.SortedStringTrie(words)
		pos, _len, last, res = 0, len(text), '', []
		while pos < _len:
			tmp = list(trie.iter_prefixes(text[pos:]))
			if tmp:
				if last:
					res.extend(jieba.cut(last))
					last = ''
				res.append(tmp[-1])
				pos += len(tmp[-1])
			else:
				last += text[pos]
				pos += 1
		if last:
			res.extend(jieba.cut(last))
		return res

	def add_in_words(self, words, word):
		""" add word in words """
		if len(word.word) > 1 and word.flag in name_flag:
			words['all'][word.word] += 1
			if word.flag in man_flag:
				words['nr'][word.word] += 1
			elif word.flag in tuan_flag:
				words['nt'][word.word] += 1
			elif word.flag in space_flag:
				words['ns'][word.word] += 1
			else:
				words['src'][word.word] += 1

	def bad_num(self, seg_list, seg_len, pos):
		""" Is bad num """
		if pos + 1 < seg_len and seg_list[pos + 1].flag == 'm' or \
				self.next_is_english(seg_list, seg_len, pos + 1):
			return True
		return False

	def next_is_english(self, seg_list, seg_len, pos):
		""" Is next englsih """
		if pos + 1 < seg_len \
				and seg_list[pos].flag == 'eng' \
				and seg_list[pos + 1].flag == 'eng':
			return True
		if pos + 2 < seg_len \
				and seg_list[pos].flag == 'eng' \
				and seg_list[pos + 1].flag == 'x' \
				and seg_list[pos + 2].flag == 'eng':
			return True
		return False

	def add_in_compos(self, words, seg_list, seg_len, pos):
		""" add word in compos """
		if seg_list[pos].flag == 'nr' and (
				len(seg_list[pos].word) == 1 or
				pos + 1 < seg_len and len(seg_list[pos + 1].word) == 1):
			return pos

		next = pos + 1
		last = seg_list[pos].flag
		while next < seg_len:
			if seg_list[next].flag == 'n':
				last = 'n'
			elif last in man_flag and seg_list[next].flag in man_flag:
				last = seg_list[next].flag
			else:
				if re_num.match(seg_list[next].word):
					if self.bad_num(seg_list, seg_len, next):
						break
					last = 'num'
				elif seg_list[next].word == ' ' \
						and next + 1 < seg_len \
						and re_num.match(seg_list[next + 1].word):
					if self.bad_num(seg_list, seg_len, next + 1):
						break
					next += 1
					last = 'num'
				elif last == 'num' and seg_list[next].flag == 'eng':
					if self.next_is_english(seg_list, seg_len, next):
						break
					last = 'eng'
				else:
					break
			next += 1

		if next > pos + 1:
			last = ['']		
			for i in range(pos, next):
				if len(last[-1]) > 1 and len(seg_list[i].word) > 1 \
						and not re_num.match(seg_list[i].word):
					last.append('')
				last[-1] += seg_list[i].word
			for word in last:
				words['all'][word] += 1
			if len(last) > 1:
				words['all'][''.join(last)] += 1
				words['compos']['^^'.join(last)] += 1
			pos = next - 1

		return pos

	def add_in_english(self, words, seg_list, seg_len, pos):
		""" add word in english words """
		next, empty = pos + 1, 0
		while next < seg_len and next <= pos + 5 + empty and empty <= 3:
			if seg_list[next].word == ' ':
				empty += 1
			elif seg_list[next].word in '-_' \
					or re_num.match(seg_list[next].word)\
					or seg_list[next].flag == 'eng':
				pass
			else:
				word = ''.join(x.word for x in seg_list[pos:next]).strip()
				if len(word) > 1:
					words['all'][word] += 1
					words['eng'][word] += 1
				return next - 1
			next += 1

		if next == seg_len:
			word = ''.join(x.word for x in seg_list[pos:next]).strip()
			if len(word) > 1:
				words['all'][word] += 1
				words['eng'][word] += 1
		else:
			while next < seg_len and seg_list[next].flag in ['eng', 'x']:
				next += 1

		return next - 1

	def add_in_blackets(self, words, seg_list, seg_len, pos):
		""" add word in blackets words"""
		index = blackets['open'].index(seg_list[pos].word)
		next, empty = pos + 1, 0
		while next < seg_len and next <= pos + 10 + empty:
			if seg_list[pos].word != u'《' and next > pos + 5 + empty \
					or seg_list[next].word == u"《" \
					or empty > 5:
				break
			if seg_list[pos].word == ' ':
				empty += 1
			elif len(seg_list[next].word) == 1 \
					and seg_list[next].word in blackets['close'][index]:
				if next == pos + 1:
					break
				for i in range(pos + 1, next):
					self.add_in_words(words, seg_list[i])
				word = ''.join(x.word for x in seg_list[pos+1:next])
				words['all'][word] += 1
				words['blackets'][word] += 1
				return next
			next += 1
		return pos

	def seg(self, title, content):
		""" segment word from article title and content """
		title = title.encode('utf-8').decode('utf-8')
		content = content.encode('utf-8').decode('utf-8')
			
		seg_list = list(pseg.cut(content))
		seg_len = len(seg_list)
		#print ' '.join(str(word) for word in seg_list)
		words = {'all':collections.defaultdict(int)}
		words['src'] = collections.defaultdict(int)
		words['nr'] = collections.defaultdict(int)
		words['ns'] = collections.defaultdict(int)
		words['nt'] = collections.defaultdict(int)
		words['eng'] = collections.defaultdict(int)
		words['compos'] = collections.defaultdict(int)
		words['blackets'] = collections.defaultdict(int)

		pos = 0
		while pos < seg_len:
			last, word = pos, seg_list[pos]
			if pos + 1 < seg_len:
				if word.flag in compos_flag or \
						word.flag == 'eng' and seg_list[pos + 1].flag in ['n']:
					pos = self.add_in_compos(words, seg_list, seg_len, pos)
				elif word.flag == 'uj' and seg_list[pos + 1].flag in ['a','v']:
					pos = self.add_in_compos(words, seg_list, seg_len, pos + 1)
				elif word.flag == 'eng' or re_num.match(word.word) and (
							seg_list[pos + 1].flag == 'eng' or 
							pos + 2 < seg_len and
							seg_list[pos + 1].flag == 'x' and 
							seg_list[pos + 2].flag == 'eng'):
					pos = self.add_in_english(words, seg_list, seg_len, pos)
				elif len(word.word) == 1 and word.word in blackets['open']:
					pos = self.add_in_blackets(words, seg_list, seg_len, pos)
			if last == pos:
				self.add_in_words(words, word)
			pos += 1

		words['title'] = self.cut(title, words['all'])
		self.clean(words)
		return words

	def clean(self, words):
		words['all'] = dict(filter(lambda x: '.com' not in x[0].lower(), words['all'].iteritems()))
		words['src'] = dict(filter(lambda x: '.com' not in x[0].lower(), words['src'].iteritems()))
		words['eng'] = dict(filter(lambda x: '.com' not in x[0].lower(), words['eng'].iteritems()))


segmentor = Segmentor()


class KeywordTest(unittest.TestCase):

	def test_cut(self):
		pass
		# utils.print_list(keyword.cut('安倍在“海之日”前发表讲话 称将维护海洋权益'))
		# utils.print_list(keyword.cut('广州4名小学女生同遭性侵 被要求读淫秽日记'))
		# utils.print_list(keyword.cut('潮州男子车祸后性功能受损 妻索“性福权”'))
		# utils.print_list(keyword.cut('遊客夫妻涉嫌在雲南大理客棧殺女兒後投洱海自盡'))

	def test_seg(self):

		@utils.atime('test seg with name')
		def test_seg_with_name(name):
			article = utils.load_json(name)
			words = segmentor.seg(article['title'], article['content'])
			print '+' * 120
			print 'article:', article['title']
			# print 'content:', article['content']
			utils.print_dict(words['all'], 'all words', cmp_key=lambda x: x[1])
			utils.print_dict(words['src'], 'src words', cmp_key=lambda x: x[1])
			utils.print_dict(words['nr'], 'nr words', cmp_key=lambda x: x[1])
			utils.print_dict(words['ns'], 'ns words', cmp_key=lambda x: x[1])
			utils.print_dict(words['nt'], 'nt words', cmp_key=lambda x: x[1])
			utils.print_dict(words['eng'], 'eng words', cmp_key=lambda x: x[1])
			utils.print_dict(words['compos'], 'compos words', cmp_key=lambda x: x[1])
			utils.print_dict(words['blackets'], 'blackets words', cmp_key=lambda x: x[1])
			print ' '.join(words['title'])
			print len(json.dumps(words))

		test_seg_with_name('keyword.test.json')
		test_seg_with_name('keyword.test.json.1')
		test_seg_with_name('keyword.test.json.2')
		test_seg_with_name('keyword.test.json.3')
		test_seg_with_name('keyword.test.json.4')


if __name__ == '__main__':
	unittest.main()