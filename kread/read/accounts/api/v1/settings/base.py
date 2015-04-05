# coding: utf-8
import os
import conf

DEBUG = True
APPID = 2001

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FOLDER = conf.templates_root + '/accounts'
STATIC_FOLDER = conf.media_root + '/accounts'

ALL_ERROR_JSON = True

SESSION_COOKIE_NAME = 'api.acounts.session'
SECRET_KEY = 'SECRET KEY'
PASSWORD_SECRET = 'PASSWORD SECRET'
WTF_CSRF_SECRET_KEY = 'WTF CSRF SECRET KEY'

SQLITE_FILE = os.path.join(ROOT_FOLDER, 'db.sqlite')
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % SQLITE_FILE

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(conf.data_root, 'admin-cache')

SERVICE_EMAIL = 'service@haoku.net'

EMAIL_TOKEN_TIME_LIMIT = 86400 * 3
ACCESS_EMAIL_URL = 'http://0.0.0.0:3001/profile/bind_email'
RESET_EMAIL_URL = 'http://0.0.0.0:3001/users/reset_pass'

TOKEN_TIMEOUT_LIMIT = 86400 * 90
DEFAULT_AVATAR = 'default.jpg'

API_HOSTS = {
	2001: 'http://0.0.0.0:2001/access',
	2002: 'http://0.0.0.0:2002/access',
}

SSO_HOSTS = {
	3002: 'http://0.0.0.0:3002/access',
	3003: 'http://0.0.0.0:3003/access',
}

SSO_LOGOUT_HOSTS = {
	3002: 'http://0.0.0.0:3002/logout',
	3003: 'http://0.0.0.0:3003/logout',
}
