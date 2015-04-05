# coding: utf-8
import conf

DEBUG = False

STATIC_FOLDER = conf.media_root + '/accounts/dist'

SECRET_KEY = '90f14971ebf9c75bec13751faec92cd00924f081e451721d3f80a2f5bd8c9fff'
PASSWORD_SECRET = '159233dc77f2d60b7380b00ecffd857cf74f37febfeb53e8b7594293df679602'
WTF_CSRF_SECRET_KEY = 'b6ac6064b1162e401688a9b8633d5419f018ade11ef0d69c4f35cf15506410f1'

CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'haocool.net'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_PASSWORD = ''
CACHE_REDIS_DB = 10

ACCESS_EMAIL_URL = 'http://accounts.test.haoku.net/profile/bind_email'
RESET_EMAIL_URL = 'http://accounts.test.haoku.net/users/reset_pass'

API_HOSTS = {
	2001: 'http://api.accounts.test.haoku.net/access',
	2002: 'http://api.test.haoku.net/access',
}

SSO_HOSTS = {
	3002: 'http://bbs.test.haoku.net/access',
	3003: 'http://test.haoku.net/access',
}

SSO_LOGOUT_HOSTS = {
	3002: 'http://bbs.test.haoku.net/logout',
	3003: 'http://test.haoku.net/logout',
}
