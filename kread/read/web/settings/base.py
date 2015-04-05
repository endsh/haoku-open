# coding: utf-8
import os
import conf

DEBUG = True
APPID = 3003

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FOLDER = conf.templates_root + '/read'
STATIC_FOLDER = conf.media_root + '/read'

SESSION_COOKIE_NAME = 'www.session'
SECRET_KEY = 'SECRET KEY'
PASSWORD_SECRET = 'PASSWORD SECRET'
WTF_CSRF_SECRET_KEY = 'WTF CSRF SECRET KEY'

SQLITE_FILE = 'db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % SQLITE_FILE

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(conf.data_root, 'admin-cache')
