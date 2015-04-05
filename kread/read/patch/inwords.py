# coding: utf-8
import conf
from db import MongoGetter
from utils import load_json
from .cmd import *
			

@local()
def update():
	mongo = MongoGetter(conf.mongo_spider)
	mongo.word.drop()

	words = load_json('words.json')['best']

	count = 0
	for word in words:
		mongo.word.save({'_id':word, 'cmd':0})
		count += 1
		if count % 1000 == 0:
			print count


if __name__ == '__main__':
	main()
