# coding: utf-8
import time
from index.topic import test_topic
from .cmd import *


@remote('test_topics')
def remote_topics():
	return test_topic()


if __name__ == '__main__':
	main()