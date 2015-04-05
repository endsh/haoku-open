# coding: utf-8
import time
from utils import atime
from .base import web
from .cmd import *


@atime('index')
def upgrade_index(key, index):
	count = 0
	good = 0
	for row in index.find():
		good += web.reindex.add(row)
		count += 1
		if count % 10000 == 0:
			print 'upgrade %s finish %d:%d' % (key, count, good)
	return count


@remote()
@atime('upgrade')
def upgrade():
	for key, index in web.index.indexs.iteritems():
		print 'upgrade %s start ...' % key
		count = upgrade_index(key, index)
		print 'upgrade %s all finish %d' % (key, count)


if __name__ == '__main__':
	main()
