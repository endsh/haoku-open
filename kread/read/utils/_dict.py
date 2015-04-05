# coding: utf-8
import unittest


class Key2Attr(dict):

	def __getattr__(self, name):
		if name in self.__dict__:
			return self.__dict__[name]
		return self[name]


def key2attr(_dict):
	return Key2Attr(_dict)


class Key2AttrTest(unittest.TestCase):

	def test_key2attr(self):
		obj = key2attr({'a':1, 'b':2})
		self.assertEqual(obj.a, 1)
		self.assertEqual(obj.b, 2)


if __name__ == '__main__':
	unittest.main()