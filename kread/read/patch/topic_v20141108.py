# coding: utf-8
import time
from index.topic import get_topics
from .cmd import *


@remote('topics')
def remote_topics():
	return get_topics()


if __name__ == '__main__':
	main()