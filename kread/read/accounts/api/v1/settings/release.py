# coding: utf-8
import conf

DEBUG = False

STATIC_FOLDER = conf.media_root + '/accounts/dist'

SECRET_KEY = 'c06e5416b8a0fa6c6364c2d8f58a1afbcfc3c6e50d7e5b3384830b27751582dc'
PASSWORD_SECRET = '66e132fbe6750c6c888859d20a7821c8743078893a4e276738ebdeede727de66'
WTF_CSRF_SECRET_KEY = '1d508d6b3f8d3129a8bb8c84fe1897f8b7f96d95911f76bad09e028992b27116'

CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = 'haocool.net'
CACHE_REDIS_PORT = 6379
CACHE_REDIS_PASSWORD = ''
CACHE_REDIS_DB = 0

SQLALCHEMY_DATABASE_URI = ''

ACCESS_EMAIL_URL = 'http://accounts.haoku.net/profile/bind_email'
RESET_EMAIL_URL = 'http://accounts.haoku.net/users/reset_pass'

API_HOSTS = {
	2001: 'http://api.accounts.haoku.net/v1/access',
	2002: 'http://api.haoku.net/v1/access',
}

SSO_HOSTS = {
	3002: 'http://bbs.haoku.net/access',
	3003: 'http://www.haoku.net/access',
}

SSO_LOGOUT_HOSTS = {
	3002: 'http://bbs.haoku.net/logout',
	3003: 'http://www.haoku.net/logout',
}
