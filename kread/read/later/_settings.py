# coding: utf-8
import os
import conf

DEBUG = not conf.RELEASE

REGISTER_OPEN = True
VERIFY_EMAIL = True
VERIFY_USER = True

ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = conf.media_root + '/later/'
if not DEBUG:
	STATIC_FOLDER = conf.media_root + '/later/dist'

SITE_TITLE = 'HaoKu Simin'
SITE_URL = '/'

SECRET_KEY = 'secret key'
PASSWORD_SECRET = 'password secret key'

SQLITE_FILE = 'db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % SQLITE_FILE
SQLALCHEMY_ECHO = True

MONGODB_SETTINGS = {
	'db': 'later',
	'host': '127.0.0.1',
	'port': 27018,
}

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(conf.data_root, 'admin-cache')
