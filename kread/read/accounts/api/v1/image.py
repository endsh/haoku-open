# coding: utf-8
from flask import current_app


def avatar2url(path, size=None):
	if current_app.status != 'DEBUG':
		if current_app.status == 'RELEASE':
			url = 'http://avatar.haoku.net/%s' % path
		else:
			url = 'http://avatar-test.haoku.net/%s' % path
		if size == 'origin':
			url += '@95Q.jpg'
		elif size == 'big':
			url += '@120w_120h_1c_1e.jpg'
		elif size == 'normal':
			url += '@100w_100h_1c_1e.jpg'
		elif size == 'small':
			url += '@64w_64h_1c_1e.jpg'
		return url
	else:
		return 'http://0.0.0.0:3001/avatar/%s' % path
