# coding: utf-8
import conf


ACCOUNTS_API_V1_HOST = ACCOUNTS_API_V1_HOST_HTTPS = '0.0.0.0:2001'
if conf.STATUS == 'RELEASE':
	ACCOUNTS_API_V1_HOST = 'api.accounts.haoku.net/v1'
elif conf.STATUS == 'TEST':
	ACCOUNTS_API_V1_HOST = 'api.accounts.test.haoku.net/v1'