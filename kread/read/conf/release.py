# coding: utf-8

# oss config
oss_html = {
	'host': 'oss-cn-qingdao-internal.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': '',
	'link': '',
}

oss_img = {
	'host': 'oss-cn-qingdao-internal.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': '',
	'link': 'http://img.haoku.net/',
}

oss_word = {
	'host': 'oss-cn-qingdao-internal.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': '',
}

oss_text = {
	'host': 'oss-cn-qingdao-internal.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': 'hktext',
}

# mongo config
mongo_spider = {
	'host': 'coolnote.cn:27018',
	'user': 'root',
	'password': '',
	'use_greenlets': True,
	'storage': 'oss',
	'html_file': oss_html,
	'word_file': oss_word,
	'text_file': oss_text,
}

mongo_web = {
	'host': 'haocool.net:27017',
	'user': '',
	'password': '',
	'use_greenlets': True,
	'storage': 'oss',
	'image_file': oss_img,
	'text_file': oss_text,
}

mongo_iweb = {
	'host': 'coolnote.cn:29999,haoku.net:29999,haocool.net:29999,51ku.net:29999',
	'user': '',
	'password': '',
	'use_greenlets': True,
	'storage': 'oss',
	'image_file': oss_img,
	'html_file': oss_html,
	'word_file': oss_word,
	'text_file': oss_text,
}

redis_tag = {
	'host': '51ku.net',
	'port': 6379,
	'password': '',
	'db': 0,
}

redis_word = {
	'host': 'formatter.org',
	'port': 6379,
	'password': '',
	'db': 0,
}

redis_word_new = {
	'host': 'chiki.org',
	'port': 6379,
	'password': '',
	'db': 0,
}

redis_url = {
	'host': 'chiki.org',
	'port': 6379,
	'password': '',
	'db': 0,
}

redis_time = {
	'host': 'chiki.org',
	'port': 6379,
	'password': '',
	'db': 1,
}


# kserver config
fetch_conf = {
	'listener': ('haoku.net', 47001),
	'password': '',
}

handle_conf = {
	'listener': ('haoku.net', 47002),
	'password': '',
}

count_conf = {
	'listener': ('haoku.net', 47003),
}