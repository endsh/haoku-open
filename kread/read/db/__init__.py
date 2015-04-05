# coding: utf-8
import conf
from utils import cmd
from .spider import *
from .web import *
from .iweb import *
from .other import *
from .admin import *

@cmd('mongo-spider-clear')
def mongo_spider_clear():
	if conf.RELEASE == False:
		mongo = MongoSpider(conf.mongo_spider)
		mongo.clear()


@cmd('mongo-spider-clear-db')
def mongo_spider_clear_db():
	if conf.RELEASE == False:
		mongo = MongoSpider(conf.mongo_spider)
		mongo.clear_db()


@cmd('mongo-spider-clear-file')
def mongo_spider_clear_file():
	if conf.RELEASE == False:
		mongo = MongoSpider(conf.mongo_spider)
		mongo.clear_file()
