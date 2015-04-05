# coding: utf-8
import conf


SSO_TEMPLATE_FOLDER = conf.templates_root + '/sso'

ACCOUNTS_HOST = 'http://0.0.0.0:3001'
if conf.STATUS == 'RELEASE':
	ACCOUNTS_HOST = 'http://accounts.haoku.net'
elif conf.STATUS == 'TEST':
	ACCOUNTS_HOST = 'http://accounts.test.haoku.net'


ACCOUNTS_REGISTER 		= ACCOUNTS_HOST + '/users/register'
ACCOUNTS_REGISTER_AJAX 	= ACCOUNTS_HOST + '/users/register?ajax'
ACCOUNTS_LOGIN 			= ACCOUNTS_HOST + '/users/login'
ACCOUNTS_LOGIN_AJAX		= ACCOUNTS_HOST + '/users/login?ajax'
ACCOUNTS_LOGOUT			= ACCOUNTS_HOST + '/users/logout'
ACCOUNTS_PROFILE		= ACCOUNTS_HOST + '/profile'
ACCOUNTS_PASSWD			= ACCOUNTS_HOST + '/profile/change_pass'


WEB_HOST = 'http://0.0.0.0:3003'
if conf.STATUS == 'RELEASE':
	WEB_HOST = 'http://www.haoku.net'
elif conf.STATUS == 'TEST':
	WEB_HOST = 'http://test.haoku.net'

WEB_LATEST				= WEB_HOST + '/latest'
WEB_SEARCH_URL			= WEB_HOST + '/topics'
WEB_ABOUT_US			= WEB_HOST + '/about'
WEB_ABOUT_JOIN			= WEB_HOST + '/about/join'
WEB_ABOUT_MEDIA			= WEB_HOST + '/about/media'
WEB_ABOUT_LINK			= WEB_HOST + '/about/link'
WEB_ABOUT_CONTACT		= WEB_HOST + '/about/contact'
WEB_ABOUT_UPDATE		= WEB_HOST + '/about/update'