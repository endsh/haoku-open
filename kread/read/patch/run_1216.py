# coding: utf-8
from gevent import monkey; monkey.patch_socket()
import pymongo
import conf
import gevent.pool
import json
import redis
import sys
import hashlib
import math
import urllib
from collections import OrderedDict
from index import Keyword
from utils import unicode2hash, hash2long, html2doc, doc2html
from .base import spider, find2do, iweb
from .cmd import *

@remote()
def upgrade():
	iweb.catecory.create_index([
		('domain', pymongo.ASCENDING),
		('status', pymongo.ASCENDING),
		('next', pymongo.ASCENDING),
	])

	iweb.template.create_index([
		('domain', pymongo.ASCENDING),
		('status', pymongo.ASCENDING),
	])

	iweb.domain.create_index('status', pymongo.ASCENDING)



if __name__ == '__main__':
	main()
