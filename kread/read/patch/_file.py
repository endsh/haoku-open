# coding: utf-8
from utils import save_json

__all__ = [
	'up', 'down', 'ups', 'downs',
]

_path = 'patch/'
_ups = set()
_downs = set()


def up(name):
	_ups.add('%s.json' % name)
	def wrapper(func):
		def new_func(*args, **kwargs):
			res = func(*args, **kwargs)
			save_json(_path + '%s.json' % name, res)
			return res
		return new_func
	return wrapper


def down(name):
	_downs.add('%s.json' % name)
	def wrapper(func):
		def new_func(*args, **kwargs):
			res = func(*args, **kwargs)
			save_json(_path + '%s.json' % name, res)
			return res
		return new_func
	return wrapper


def ups():
	return _ups


def downs():
	return _downs