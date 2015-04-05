# coding: utf-8
import os
import conf

DEBUG = True
APPID = 3002

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FOLDER = conf.templates_root + '/bbs'
STATIC_FOLDER = conf.media_root + '/bbs'

SECRET_KEY = 'SECRET KEY'
SESSION_COOKIE_NAME = 'bbs.session'
PASSWORD_SECRET = 'PASSWORD SECRET'
WTF_CSRF_SECRET_KEY = 'WTF CSRF SECRET KEY'

# CACHE_TYPE = 'filesystem'
# CACHE_DIR = os.path.join(conf.data_root, 'web-cache')