# coding: utf-8
import unittest


def u(text):
	""" auto text encode unicode """
	return unicode(text, 'utf-8') if type(text) is str else text


def t(text):
	""" auto text encode utf-8 """
	return text.encode('utf-8') if type(text) is unicode else text


class CharTest(unittest.TestCase):

	def test_u(self):
		self.assertEqual(len(u('python shell是什么东西_百度知道。')), 23)
		self.assertEqual(len(u(u'python shell是什么东西_百度知道。')), 23)

	def test_t(self):
		self.assertEqual(len(t('python shell是什么东西_百度知道。')), 43)
		self.assertEqual(len(t(u'python shell是什么东西_百度知道。')), 43)


if __name__ == '__main__':
	unittest.main()