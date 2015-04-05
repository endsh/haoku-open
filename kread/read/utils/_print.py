# coding: utf-8
import unittest
import utils


def print_list(_list, title=None, key=None, sep='  ', sort=False, cmp_key=None, cmp=None):
	""" print list """
	if not _list:
		return
	_list = [key(x) for x in _list] if key else _list
	if sort or cmp_key or cmp:
		_list = sorted(_list, key=cmp_key, reverse=True if sort < 0 else False, cmp=cmp)
	_list = [utils.u(x) if type(x) is str else unicode(x) for x in _list]
	_len = max([utils.chinese_count(x) + len(x) for x in _list])
	tpl = u'{:<%d}'
	tpl_format = lambda x: (tpl % (_len - utils.chinese_count(x))).format(x)
	step = max(120 / (_len + len(sep)), 1)
	lines = [_list[i:i+step] for i in range(0,len(_list),step)]
	print '=' * 120 + '\n' + title + '\n' + '-' * 120 if title else '=' * 120
	print u'\n'.join(sep.join([tpl_format(i) for i in x]) for x in lines)


def print_dict(_dict, title=None, key=None, value=None, sep=' '*4, 
		key_sep=' ', sort=False, cmp_key=None, cmp=None, limit=0):
	""" print dict """
	if not _dict:
		return
	_dict = dict((key(k), v) for k, v in _dict.iteritems()) if key else _dict
	_dict = dict((k, value(v)) for k, v in _dict.iteritems()) if value else _dict
	if not sort and not cmp_key and not cmp:
		keys, values = _dict.keys(), _dict.values()
	else:
		_dict = sorted(_dict.iteritems(), key=cmp_key, reverse=True if sort < 0 else False, cmp=cmp)
		if limit > 0:
			_dict = _dict[:limit]
		keys, values = [x for x,_ in _dict], [x for _,x in _dict]
	keys = [utils.u(x) if type(x) is str else unicode(x) for x in keys]
	key_len = max([utils.chinese_count(x) + len(x) for x in keys])
	values = [utils.u(x) if type(x) is str else unicode(x) for x in values]
	value_len = max([utils.chinese_count(x) + len(x) for x in values])
	tpl = u'{:<%d}' + key_sep + '{:<%d}'
	tpl_format = lambda i, x:(tpl % (
		key_len - utils.chinese_count(x[0][i]), 
		value_len - utils.chinese_count(x[1][i]))).format(x[0][i], x[1][i])
	step = max(120 / (key_len + value_len + 2 + len(sep)), 1)
	lines = [[keys[i:i+step], values[i:i+step]] for i in range(0,len(keys),step)]
	print ('=' * 120 + '\n' + title + '\n' + '-' * 120 if title else '=' * 120).encode('utf-8')
	print ('\n'.join(sep.join([tpl_format(i, x) for i in range(len(x[0]))]) for x in lines)).encode('utf-8')


class PrintTest(unittest.TestCase):

	def random_chinese_list(self, _len=100):
		import random
		words = []
		for i in range(_len):
			words.append(u''.join(random.choice(u'一二三四五六七八九十百千万')
				for j in range(2, random.choice(range(3, 8)))))
		return words

	def test_print_list_with_chinese(self):
		_list = self.random_chinese_list()
		print_list(_list, 'test print list with chinese')
		print_list(_list, 'test print list with chinese on sort', sort=-1)

	def test_print_dict_with_chinese(self):
		_dict = dict(zip(self.random_chinese_list(), range(1000, 10, -10)))
		print_dict(_dict, 'test print dict with chinese')
		print_dict(_dict, 'test print dict with chinese on key', key=lambda x:x+u'a')
		print_dict(_dict, 'test print dict with chinese on sort', sort=-1)
		def cmp_test(x, y):
			res = cmp(x[0][0], y[0][0])
			if res:
				return res
			return cmp(len(x[0]), len(y[0]))
		print_dict(_dict, 'test print dict with chinese on cmp', sort=1, cmp=cmp_test)

	def test_print_list(self):
		_list = range(1000, 10000, 50)
		print_list(_list, 'test print list')
		print_list(_list, 'test print list on key', key=lambda x:x+1)
		print_list(_list, 'test print list on sep', key=lambda x:str(x)+'y', sep=' *** ')
		print_list(_list, 'test print list on sort', key=lambda x:x+1, sort=-1)

	def test_print_dict(self):
		_dict = dict(zip(range(1000, 10000, 50), range(1000, 10, -5)))
		print_dict(_dict, 'test print dict')
		print_dict(_dict, 'test print dict on key', key=lambda x:x+1)
		print_dict(_dict, 'test print dict on value', value=lambda x:str(x)+'y')
		print_dict(_dict, 'test print dict on sep', value=lambda x:str(x)+'y', sep=' *** ')
		print_list(_dict, 'test print dict on sort', key=lambda x:x+1, sort=-1)


if __name__ == '__main__':
	unittest.main()