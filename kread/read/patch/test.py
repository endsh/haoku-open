# coding: utf-8
import time
from .cmd import *


@local('local_test')
def local_test():
	return {'msg':'local_test at time %d.' % time.time()}


@remote('remote_test')
def remote_test():
	return {'msg':'remote_test at time %d.' % time.time()}


if __name__ == '__main__':
	main()