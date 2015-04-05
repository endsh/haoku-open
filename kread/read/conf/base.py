# coding: utf-8
from os.path import dirname, abspath


# common config
root = dirname(dirname(dirname(abspath(__file__))))
data_root = root + '/data'
logs_root = root + '/logs'
test_root  = data_root + '/test'

media_root = root + '/media'
templates_root = root + '/templates'

# oss config
oss_html = {
	'host': 'oss-cn-qingdao-a.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': '',
	'link': '',
}

oss_img = {
	'host': 'oss-cn-qingdao-a.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': 'hkimg',
	'link': 'http://img.haoku.net/',
}

html_file = {
	'path':'scheduler/html',
	'prefix':'',
}

image_file = {
	'path':'scheduler/image',
	'prefix':'',
}

word_file = {
	'path':'scheduler/word',
	'prefix':'',
}

text_file = {
	'path':'scheduler/text',
	'prefix':'',
}

# mongo config
mongo_spider = {
	'host': 'localhost:27018',
	'user': '',
	'password': '',
	'use_greenlets': True,
	'storage': 'local',
	'html_file': html_file,
	'word_file': word_file,
	'text_file': text_file,
}

mongo_web = {
	'host': 'localhost:27017',
	'user': '',
	'password': '',
	'use_greenlets': True,
	'storage': 'local',
	'image_file': image_file,
	'text_file': text_file,
}

mongo_iweb = {
	'host': 'localhost:27018',
	'user': '',
	'password': '',
	'use_greenlets': True,
	'storage': 'local',
	'image_file': image_file,
	'html_file': html_file,
	'word_file': word_file,
	'text_file': text_file,
}


# redis config
redis_rss = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 0,
}

redis_tag = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 1,
}

redis_word = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 2,
}

redis_meta = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 3,
}

redis_index = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 4,
}

redis_log = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 5,
}

redis_url = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 6,
}

redis_cluster = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 7,
}

redis_topic = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 8,
}

redis_time = {
	'host': 'localhost',
	'port': 6379,
	'password': '',
	'db': 9,
}


# kserver config
fetch_conf = {
	'listener': ('localhost', 47001),
	'password': '',
}

handle_conf = {
	'listener': ('localhost', 47002),
	'password': '',
}

count_conf = {
	'listener': ('localhost', 47003),
}
