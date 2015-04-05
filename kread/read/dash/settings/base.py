# coding: utf-8
import os
import conf


DEBUG = True
TESTING = False

REGISTER_OPEN = True
VERIFY_EMAIL = True
VERIFY_USER = True

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = conf.media_root + '/dash'

SITE_TITLE = u'好酷仪表盘'
SITE_URL = '/'
WEB_TEST_URL = 'http://127.0.0.1:3003/'

SECRET_KEY = 'SECRET KEY'
PASSWORD_SECRET = 'PASSWORD SECRET'

SQLITE_FILE = 'db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % SQLITE_FILE
SQLALCHEMY_ECHO = False

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(conf.data_root, 'admin-cache')
