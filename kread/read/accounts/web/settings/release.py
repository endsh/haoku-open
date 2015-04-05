# coding: utf-8
import conf

DEBUG = False

STATIC_FOLDER = conf.media_root + '/accounts/dist'

SECRET_KEY = '31bb32c04140567ffb447d787768c648122dda2c9adfcc00903630e677263519'
PASSWORD_SECRET = '8306366c9c9e1eca1b422c82569a51af92f041826a50e48c81e0bc36884b9c8b'
WTF_CSRF_SECRET_KEY = 'f78871125d7aafc07e04a1215f9e948c90ef6ac57c68af13ec84d047b9139010'

CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'haocool.net'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_PASSWORD = ''
CACHE_REDIS_DB = 1

AVATAR_FILE_CONF = {
	'host': 'oss-cn-qingdao-internal.aliyuncs.com',
	'access_id': '',
	'secret_access_key': '',
	'bucket': 'hkavatar',
	'link': 'http://avatar.haoku.net/',
}
