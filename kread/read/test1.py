# coding: utf-8
import re
from utils import get_or_cache, print_list
from contextlib import contextmanager


@contextmanager
def get2do(dkey=None):
	print 'c'
	yield dkey
	print 'd'


class A:

	@contextmanager
	def get(self, dkey):
		print 'c'
		yield dkey
		print 'd'


c = A()


with c.get(dkey=1) as a:
	print a

with c.get(dkey=2) as a:
	print a


