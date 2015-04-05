# coding: utf-8
import os
import conf


DEBUG = False
TESTING = False

REGISTER_OPEN = False
VERIFY_EMAIL = True
VERIFY_USER = True

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = conf.media_root + '/dash/dist'

SITE_TITLE = u'好酷仪表盘'
SITE_URL = '/'
WEB_TEST_URL = 'http://www.haoku.net/'

SECRET_KEY = 'Zm0WuB9M5wOh7i6cuG7x2liJespU+hY/dKvgYfYiaVpV6BmJ+0ZdqmyTBtDavGAXZ2wJag6EiMXSTVgijQ+87Q=='
PASSWORD_SECRET = 'QjUseljlDz79ZgOQxwjELefdpNFKZ7fWOQarGAQ9n0LeyLjJRpzEfVCv7eutFIDswTm+hZ0DnqymBHa0/RGIzQ=='

SQLITE_FILE = 'db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % SQLITE_FILE
SQLALCHEMY_ECHO = False

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(conf.data_root, 'admin-cache')
