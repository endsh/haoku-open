# coding: utf-8
import os
import conf

DEBUG = True
APPID = 3001

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_FOLDER = conf.templates_root + '/accounts'
STATIC_FOLDER = conf.media_root + '/accounts'

SESSION_COOKIE_NAME = 'acounts.session'
SECRET_KEY = 'SECRET KEY'
PASSWORD_SECRET = 'PASSWORD SECRET'
WTF_CSRF_SECRET_KEY = 'WTF CSRF SECRET KEY'

CACHE_TYPE = 'filesystem'
CACHE_DIR = os.path.join(conf.data_root, 'admin-cache')

AVATAR_FILE_CONF = {
	'path':'accounts/upload',
	'link': '/avatar/%s'	
}