# coding: utf-8
import os


def get_status():
	status = 'DEBUG'
	if os.environ.get('XIAOKU_STATUS') == 'RELEASE':
		status = 'RELEASE'
	elif os.environ.get('XIAOKU_STATUS') == 'TEST':
		status = 'TEST'
	return status


def get_root_folder(curr_file):
	return os.path.dirname(os.path.dirname(os.path.abspath(curr_file)))