# coding: utf-8
from __future__ import unicode_literals
from flask.ext.restful import abort as _abort

_code = 0
def code(n=None):
	if not n or type(n) != int:
		n = _code + 1
	globals()['_code'] = n
	return n


_keys = {}
_msgs = {}
def M(**kwargs):
	for key, n in kwargs.iteritems():
		globals()[key] = code(n)
		_keys[globals()[key]] = key
		_msgs[globals()[key]] = key if type(n) == int else n


def abort(code, **kwargs):
	_abort(400, code=code, key=_keys[code], msg=_msgs[code], **kwargs)


M(COMMON_START=20000)
M(SERVER_ERROR='系统出错')
M(INVALID_ARGS='参数无效')
M(ARGS_REQUIRED='参数必填')
M(UNKONWN_ERROR='未知错误')
M(API_NOT_FOUND='资源未找到')
M(ACCESS_DENIED=0)
M(ACCESS_DENIED_WITH_CLIENT=0)
M(ACCESS_DENIED_WITH_SERVICE=0)
M(ACCESS_TIMEOUT=0)
M(INVALID_TOKEN=0)
M(INVALID_TOKEN_WITH_ACCESS_TIME=0)
M(INVALID_SERVICE_ID=0)
M(INVALID_CLIENT_ID=0)
M(INVALID_CLIENT_TIME=0)
