# coding: utf-8
import conf

DEBUG = False

STATIC_FOLDER = conf.media_root + '/accounts/dist'

SECRET_KEY = 'b4f59a1bc16fd318e4ffa41e1913822fdf91439c8f3e2c47d53381ee64395060'
PASSWORD_SECRET = '1d29d224fe3ff37b8c0962462c5c3e7617781e2a13e1846809703e82b38e5e50'
WTF_CSRF_SECRET_KEY = 'e82ae0195db510f3d5b6ce0d9b38dc8e18588242d2812cd93098cf9b4750bbcd'

CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'haocool.net'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_PASSWORD = ''
CACHE_REDIS_DB = 11

AVATAR_FILE_CONF = {
	'host': 'oss-cn-qingdao-internal.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': 'hkavatar-test',
	'link': 'http://avatar-test.haoku.net/',
}
