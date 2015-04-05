# coding: utf-8
import jieba
import socket
import traceback
import time
import redis
import random
import threading
from db import MongoIWeb
from utils import PQDict
from utils._thread import Master
from spider import article, domain
from spider.cmd import handle
from spider.network import Client
from index import Keyword


class Handler(Master, Client):

	def __init__(self, conf, log):
		Master.__init__(self, log, conf['count'])
		Client.__init__(self, conf['listener'], conf['password'], log)
		self.seg = conf['seg']
		self.mongo = MongoIWeb(conf['mongo_iweb'])
		self.html_file = self.mongo.html_file
		self.image_file = self.mongo.image_file
		self.word_file = self.mongo.word_file
		self.text_file = self.mongo.text_file
		self.redis_word = redis.Redis(**conf['redis_word'])
		self.redis_tag = redis.Redis(**conf['redis_tag'])
		self.redis_time = redis.Redis(**conf['redis_time'])
		self.cluster_redis = redis.Redis(**conf['redis_cluster'])
		self.keyword = Keyword(self.redis_word)
		self.tasks = PQDict(
			key=lambda x: x.value['key'],
			score=lambda x: -x.value['info']['pubtime'] if 'pubtime' in x.value['info'] else -2000000000,
		)
		self.lock = threading.Lock()
		self.round = conf['round']
		self.limit = conf['limit']
		self.timeout = conf['timeout']
		self.name = 'handler'
		self.last = 0

	def get(self):
		if len(self.tasks):
			self.lock.acquire()
			if len(self.tasks):
				task = self.tasks.get()
			else:
				task = None
			self.lock.release()
			return task

	def update(self):
		if time.time() - self.last > 300:
			self.keyword.update()
			self.last = time.time()

	def do(self, task):
		key, cmd, info, ext = task['key'], task['cmd'], task['info'], task['ext']
		self.log.debug('handle %s: %s' % (cmd, info['url']))
		start = time.time()

		async = True
		if 'pubtime' not in task['info'] or time.time() - task['info']['pubtime'] < 300:
			async = False

		try:
			res = handle.run(cmd, self, key, info, ext)
		except KeyboardInterrupt, e:
			raise e
		except Exception, e:
			res = {'exc': e.__class__.__name__}
			self.log.warn('handle exception %s: %s' % (info['url'], str(e)))
			self.log.warn(traceback.format_exc())

		self.log.debug('handle %s success(%.2f): %s' % (cmd, time.time() - start, info['url']))
		self.results.append({'key':key, 'cmd':cmd, 'res':res, 'async':async})

	def pre_exit(self):
		#jieba.disable_parallel()
		pass

	def on_exit(self):
		self.log.info('%s on exit ...' % self.name)
		# jieba.disable_parallel()

	def load(self):
		try:
			if len(self.tasks) < self.limit:
				self.sendobj({'type':'load', 'count':self.round})
				message = self.recvobj()
				if message['tasks']:
					self.lock.acquire()
					self.tasks.extend(message['tasks'])
					self.lock.release()
				else:
					self.finish()
					self.wait(3)
				self.log.info('load %d tasks.' % len(message['tasks']))
		except socket.error, e:
			self.log.warn('load tasks socket error: %s' % str(e))
			self.close()

	def finish(self):
		try:
			results = []
			for _ in range(min(100, len(self.results))):
				results.append(self.results.pop(0))
			if results:
				self.sendobj({'type':'finish', 'results':results})
				self.log.info('finish %d tasks.' % len(results))
		except socket.error, e:
			self.log.warn('finish tasks socket error: %s' % str(e))
			self.close()

	def connect_if_need(self):
		timeout = 0
		while self.closed and not self.exited:
			self.wait(timeout)
			self.connect(seg=self.seg)
			if timeout < 5:
				timeout += 1

	def on_close(self):
		self.kill()
		self.tasks = PQDict(
			key=lambda x: x.value['key'],
			score=lambda x: -x.value['info']['pubtime'] if 'pubtime' in x.value['info'] else -2000000000,
		)
		self.results = []

	def handle(self):
		self.connect_if_need()
		self.load()
		self.finish()
		self.update()
		self.wait(self.timeout)


def main():
	import conf
	import logging
	import sys

	seg, count, full, limit, timeout = False, 5, 200, 150, 2
	level = logging.INFO
	if len(sys.argv) >= 2:
		if sys.argv[1] == 'debug':
			level = logging.DEBUG
		elif sys.argv[1] == 'realtime':
			seg, count, full, limit, timeout = False, 5, 100, 80, 1
		elif sys.argv[1] == 'segment':
			seg, count, full, limit, timeout = True, 20, 200, 100, 1

	log = logging.getLogger(__name__)
	log.setLevel(level)
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
	_handler = logging.StreamHandler()
	_handler.setLevel(level)
	_handler.setFormatter(formatter)
	log.addHandler(_handler)

	handler_conf = {
		'listener':conf.handle_conf['listener'],
		'password':conf.handle_conf['password'],
		'mongo_iweb': conf.mongo_iweb,
		'redis_word': conf.redis_word,
		'redis_tag': conf.redis_tag,
		'redis_time': conf.redis_time,
		'redis_cluster': conf.redis_cluster,
		'count':count,
		'limit':limit,
		'round':full,
		'timeout':timeout,
		'seg':seg,
	}
	handler = Handler(handler_conf, log)
	handler.run()


if __name__ == '__main__':
	main()