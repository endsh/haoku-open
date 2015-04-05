# coding: utf-8
import sys
import hashlib

__all__ = [
	'unicode2hash', 'str2hash', 'unicode2xint', 'str2xint', 'hash2long',
]


def unicode2hash(text):
	return str2hash(text.encode('utf-8'))


def str2hash(text):
	md5 = hashlib.md5(text).hexdigest()
	return hash2long(md5)


def unicode2xint(text):
	return str2xint(text.encode('utf-8'))


def str2xint(text):
	md5 = hashlib.md5(text).hexdigest()
	return hash2int(md5)


def hash2long(md5):
	return int(long(md5[8:24], 16) - sys.maxint)


def hash2int(md5):
	return int(md5[12:20], 16) - 2147483647
