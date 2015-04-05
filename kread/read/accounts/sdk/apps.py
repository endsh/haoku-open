# coding: utf-8
import hashlib

__all__ = [
	'is_app', 'is_service', 'is_client', 'app_key',
	'sncode',
]

_apps = {
	1000: {'name':'hello app.', 		'key':'6b52593a99e7b078bf21db3745dd63e7'},
	1001: {'name':'android 1.0', 		'key':'d50fcef2ba2ebfc797e82126779d077d'},
	1002: {'name':'iphone 1.0', 		'key':'c30555b2e443b041a811d1fc9c3a9122'},
	1003: {'name':'ipad 1.0', 			'key':'d6858655cdb01e08b760cb98cec6816c'},
	1004: {'name':'window 1.0', 		'key':'3d6bd9395c4148de9d100e994ff90107'},
	2000: {'name':'hello service', 		'key':'8a609b7a3e776c970d2226049356f828'},
	2001: {'name':'accounts api 1.0',	'key':'162e3253926f63e21d76d9c206267e12'},
	2002: {'name':'article api 1.0',	'key':'207bd58b3c25152fc1cd60a99e35eb6a'},
	3000: {'name':'hello site',			'key':'c89235fa45e2ac6b3d2a574fe248c094'},
	3001: {'name':'accounts.haoku.net',	'key':'7210a2551bd264f2e6195ddbd41793f7'},
	3002: {'name':'bbs.haoku.net',		'key':'1442684756e24e101f99aa2e4eee4b04'},
	3003: {'name':'www.haoku.net',		'key':'24e5429a53ddaa1ddc90be2ef19c14e7'},
	3004: {'name':'www.oslinux.cn',		'key':'7470fc41b95be6c08da0dd3c15d15d80'},
}

_services = filter(lambda x: x >= 2000, _apps.iterkeys())


def is_app(appid):
	return appid in _apps


def is_service(appid):
	return appid in _services


def is_client(appid):
	return is_app(appid) and not is_service(appid)


def app_key(appid):
	return _apps[appid]['key']


def sncode(args, key=None):
	ostr = [key] if key is not None else []
	appid = int(args.get('appid', 0))
	if not is_app(appid):
		return None

	ostr.append(app_key(appid))
	for key, value in sorted(args.iteritems(), key=lambda x: x[0]):
		if key != 'sn':
			ostr.append('%s=%s' % (key, value))
	return hashlib.md5('^^'.join(ostr).encode('utf-8')).hexdigest()
