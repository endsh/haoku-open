# coding: utf-8
import os
import json
import unittest
import conf


def load_file(path):
	""" load file """
	if os.path.isfile(path):
		with open(path) as fd:
			return fd.read()


def save_file(path, content):
	""" save file """
	fordler = path[:path.rfind('/')]
	if not os.path.exists(fordler):
		os.makedirs(fordler)
	with open(path, 'w+') as fd:
		return fd.write(content)


def remove_file(path):
	""" remove file """
	if os.path.isfile(path):
		os.remove(path)


def get_data_path(name):
	""" get data path """
	return conf.data_root + os.sep + name


def load_data(name):
	""" load data file """
	return load_file(conf.data_root + os.sep + name)


def save_data(name, content):
	""" save data file """
	return save_file(conf.data_root + os.sep + name, content)


def remove_data(name):
	return remove_file(conf.data_root + os.sep + name)


def has_data(name):
	return os.path.isfile(get_data_path(name))


def load_json(name):
	""" load json with file """
	content = load_data(name)
	if content:
		return json.loads(content)


def save_json(name, obj):
	""" save json with file """
	return save_data(name, json.dumps(obj))


class FileTest(unittest.TestCase):

	def test_load_and_save_file(self):
		path = '/home/linshao/file.test.hello.txt'
		content = 'Hello, World!'
		save_file(path, content)
		self.assertEqual(os.path.isfile(path), True)
		load_content = load_file(path)
		self.assertEqual(load_content, content)
		remove_file(path)
		self.assertEqual(os.path.exists(path), False)

	def test_load_and_save_data(self):
		name = 'file.test.hello.txt'
		content = 'Hello, World!'
		save_data(name, content)
		self.assertEqual(os.path.isfile(get_data_path(name)), True)
		load_content = load_data(name)
		self.assertEqual(load_content, content)
		remove_data(name)
		self.assertEqual(os.path.exists(get_data_path(name)), False)

	def test_load_and_save_json(self):
		name = 'file.test.json'
		obj = {'a':'Hello', 'b': 'World'}
		save_json(name, obj)
		self.assertEqual(os.path.isfile(get_data_path(name)), True)
		load_obj = load_json(name)
		self.assertEqual(load_obj, obj)
		remove_data(name)
		self.assertEqual(os.path.exists(get_data_path(name)), False)


if __name__ == '__main__':
	unittest.main()