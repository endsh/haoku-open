# coding: utf-8
import os
import conf

DEBUG = True
APPID = 2002

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FOLDER = conf.templates_root + '/api'
STATIC_FOLDER = conf.media_root + '/api'

ALL_ERROR_JSON = True

SESSION_COOKIE_NAME = 'api.session'
SECRET_KEY = 'SECRET KEY'
PASSWORD_SECRET = 'PASSWORD SECRET'
WTF_CSRF_SECRET_KEY = 'WTF CSRF SECRET KEY'

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(conf.data_root, 'admin-cache')
