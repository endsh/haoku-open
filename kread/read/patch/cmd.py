# coding: utf-8
import sys
from ._file import up, down

__all__ = [
	'local', 'remote', 'main',
]


def local(name=None):
	def wrapper(func):
		globals()['local'] = up(name)(func) if name is not None else func
		return globals()['local']
	return wrapper


def remote(name=None):
	def wrapper(func):
		globals()['remote'] = down(name)(func) if name is not None else func
		return globals()['remote']
	return wrapper


def main(default='local'):
	if len(sys.argv) >= 2 and sys.argv[1] in ['local', 'remote']:
		return globals()[sys.argv[1]](*sys.argv[2:])
	else:
		return globals()[default]()
