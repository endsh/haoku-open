# coding: utf-8
import os
import hashlib
import shutil
import conf
from .char import t
from ._file import get_data_path, has_data, load_json, save_json
from ._requests import get


def get_or_cache(url, force=False, print_path=False):
	""" get html from url or cache """
	path = '%s/%s.html' % (conf.test_root, hashlib.md5(t(url)).hexdigest())
	urls_path = conf.test_root + '/test.urls'

	if print_path:
		print path

	if not force and os.path.isfile(path):
		with open(path) as fd:
			return fd.read()

	html = get(url)
	with open(path, 'w+') as fd:
		fd.write(html)

	with open(urls_path, 'a+') as fd:
		fd.write(t(url) + '\n')
	return html


def cacheable(key, *args, **kwargs):
	def wrapper(func):
		def new_func(*xargs, **xkwargs):
			if callable(key):
				key = key(*args, **kwargs)
			return cache_key(key, func, *xargs, **xkwargs)
		return new_func
	return wrapper


def docache(handle, key, *args, **kwargs):
	return cache_key(key, handle, key, *args, **kwargs)


def cache_key(key, handle, *args, **kwargs):
	if callable(key):
		key = key(*args, **kwargs)
	# key = hashlib.md5(key).hexdigest()
	path = '%s/%s' % ('cache', key)
	if has_data(path):
		return load_json(path)

	res = handle(*args, **kwargs)
	save_json(path, res)

	return res


def create_local_cache(path):
	path = get_data_path(path)
	if os.path.exists(path):
		return

	os.mkdir(path)
	for i in '0123456789abcdef':
		ii = path + '/' + i
		os.mkdir(ii)
		for j in '0123456789abcdef':
			jj = ii + '/' + j
			os.mkdir(jj)
			for k in '0123456789abcdef':
				kk = jj + '/' + k
				os.mkdir(kk)


def drop_local_cache(path):
	path = get_data_path(path)
	if os.path.exists(path):
		shutil.rmtree(path, True)


def recreate_local_cache(path):
	drop_local_cache(path)
	create_local_cache(path)
