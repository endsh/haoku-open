# coding: utf-8
import re
import unittest
import utils


RE_CHINESE_CHAR = re.compile(u'[\u4e00-\u9fa5]')
RE_ENGLISH_CHAR = re.compile(u'\w')
RE_ENGLISH_WORD = re.compile(u'\w+')
RE_WORD = re.compile(u'[\u4e00-\u9fa5]|\w+')


def chinese_count(text):
	""" count chinese char """
	return len(RE_CHINESE_CHAR.findall(utils.u(text)))


def english_count(text):
	""" count english char """
	return len(RE_ENGLISH_CHAR.findall(utils.u(text)))


def english_word_count(text):
	""" count english word """
	return len(RE_ENGLISH_WORD.findall(utils.u(text)))


def word_count(text):
	""" count word """
	return len(RE_WORD.findall(utils.u(text)))


def sentence_count(text):
	pass


def english_sentence_count(text):
	pass


def get_chinese(text):
	return RE_CHINESE_CHAR.findall(utils.u(text))


class CountTest(unittest.TestCase):

	def test_chinese_count(self):
		self.assertEqual(chinese_count('python shell是什么东西_百度知道。'), 9)
		self.assertEqual(chinese_count('真TM像：最精致的山寨iPhone 6上手视频'), 12)
		self.assertEqual(chinese_count('hello, world!'), 0)

	def test_english_count(self):
		self.assertEqual(english_count('python shell是什么东西_百度知道。'), 12)
		self.assertEqual(english_count('真TM像：最精致的山寨iPhone 6上手视频'), 9)
		self.assertEqual(english_count('hello, world!'), 10)

	def test_english_word_count(self):
		self.assertEqual(english_word_count('python shell是什么东西_百度知道。'), 3)
		self.assertEqual(english_word_count('真TM像：最精致的山寨iPhone 6上手视频'), 3)
		self.assertEqual(english_word_count('hello, world!'), 2)

	def test_word_count(self):
		self.assertEqual(word_count('python shell是什么东西_百度知道。'), 12)
		self.assertEqual(word_count('真TM像：最精致的山寨iPhone 6上手视频'), 15)
		self.assertEqual(word_count('hello, world!'), 2)


if __name__ == '__main__':
	unittest.main()