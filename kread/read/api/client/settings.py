# coding: utf-8
import conf


API_V1_HOST = '0.0.0.0:2002'
if conf.STATUS == 'RELEASE':
	API_V1_HOST = 'api.haoku.net/v1'
elif conf.STATUS == 'TEST':
	API_V1_HOST = 'api.test.haoku.net/v1'