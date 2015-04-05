# coding: utf-8
from gevent import monkey; monkey.patch_socket()
import json
import time
import gevent
import redis
import SimpleXMLRPCServer
from collections import defaultdict
from gevent.queue import Queue, Empty
from db import MongoIWeb
from utils import BaseWorker, Worker, Group, logger
from spider.adapter import Adapter
from spider.articles import Articles
from spider.domains import Domains
from spider.server import TaskServer
from spider.topics import Topics


class SyncHandler(Worker):

	def __init__(self, master, timeout=1):
		super(SyncHandler, self).__init__(
			master, log=master.log, timeout=timeout)
		self.master = master
		self.domains = master.domains
		self.articles = master.articles

	def handle(self):
		self.domains.sync()
		self.articles.sync()

	def on_quit(self):
		self.domains.quit()
		self.articles.quit()
		self.domains.sync(quit=True)
		self.articles.sync(quit=True)


class ASyncHandler(Group):

	def __init__(self, master, count=100, waitout=0.1):
		super(ASyncHandler, self).__init__(
			master, log=master.log, count=count, timeout=1)
		self.master = master
		self.queue = Queue()
		self.waitout = waitout
		self._size = 0
		self._last = 0

	def size(self):
		if time.time() - self._last < 1:
			return self._size
		self._last = time.time()
		self._size = self.queue.qsize()
		return self._size

	def do(self, func, *args, **kwargs):
		if self.size() < 500:
			self.queue.put((func, args, kwargs))
		else:
			func(*args, **kwargs)

	def quick(self, limit=50):
		count = 0
		while count < limit:
			try:
				func, args, kwargs = self.queue.get_nowait()
				func(*args, **kwargs)
				count += 1
			except Empty:
				break

	def handle(self):
		count = 0
		while True:
			try:
				func, args, kwargs = self.queue.get()
				func(*args, **kwargs)
				count += 1
			except Empty:
				break

		self.wait(self.waitout)

	def on_quit(self):
		if not self.queue.empty():
			self.log.info('%s - has %d tasks not done. now doing ...' 
				% (self.name, self.queue.qsize()))

			# count = 0
			# while not self.queue.empty():
			# 	func, args, kwargs = self.queue.get()
			# 	func(*args, **kwargs)
			# 	count += 1
			# 	if count % 100 == 0:
			# 		self.log.done('done %d tasks, has %d tasks wait.' 
			# 			% (count, self.queue.qsize()))

			# self.log.info('%s - all done.' % self.name)


class Counter(object):

	def __init__(self, master):
		self.master = master
		self.domains = self.master.domains
		self.articles = self.master.articles
		self.async = self.master.async
		self.log = master.log
		self.count = defaultdict(int)
		self.number = defaultdict(int)
		self.last = time.time()
		self.handle()

	def add(self, key, value=1):
		self.number[key] += value
		self.count[key] += value

	@property
	def doing(self):
		res = self.domains.counter
		res.update(self.articles.counter)
		return res

	@property
	def other(self):
		return {'async':self.async.size()}

	def handle(self):
		self.json = json.dumps({
			'count':self.count, 
			'number':self.number, 
			'doing':self.doing,
			'other':self.other,
		})
		self.number.clear()
		self.last = time.time()

	def data(self):
		return self.json

	def dump(self, attrs):
		obj = self.master
		for attr in attrs.split('.'):
			keys = attr.split(':')
			key = keys[0]
			if hasattr(obj, key):
				obj = getattr(obj, key)
			else:
				return '%s not has attr %s' % (str(obj), attr)

			for key in keys[1:]:
				key = key.replace('$', '.')
				if key in obj:
					obj = obj[key]
		
		if hasattr(obj, 'dump'):
			obj = obj.dump()

		if type(obj) in (str, unicode):
			return obj

		try:
			return json.dumps(obj, indent=4)
		except Exception, e:
			return str(e)

	def imgs(self):
		return self.master.articles.img_arts.check()

	def quit(self):
		pass


class CountServer(Worker):

	def __init__(self, master, timeout=0.5):
		super(CountServer, self).__init__(
			master, log=master.log, timeout=timeout)
		from gevent import monkey
		monkey.patch_all()
		self.master = master
		self.conf = self.master.conf.count_conf
		self.domains = master.domains
		self.articles = master.articles
		self.server = SimpleXMLRPCServer.SimpleXMLRPCServer(self.conf['listener'])
		self.server.register_instance(self.master.counter)

	def loop(self):
		self.server.serve_forever()

	def on_quit(self):
		pass


class Master(BaseWorker):

	def __init__(self, conf, log):
		super(Master, self).__init__(log, term=True)
		self.conf = conf
		self.mongo = MongoIWeb(conf.mongo_iweb)
		self.redis_word = redis.Redis(**conf.redis_word)
		self.redis_tag = redis.Redis(**conf.redis_tag)
		self.redis_topic = redis.Redis(**conf.redis_topic)
		self.async = ASyncHandler(self)
		self.fetch_adapter = Adapter(self, 'fetch_adapter')
		self.handle_adapter = Adapter(self, 'handle_adapter')
		self.domains = Domains(self)
		self.articles = Articles(self)
		self.topics = Topics(self)
		self.sync = SyncHandler(self)
		self.fetchers = TaskServer(
			master=self, 
			adapter=self.fetch_adapter, 
			listener=conf.fetch_conf['listener'], 
			password=conf.handle_conf['password'],
			log=self.log,
			name='fetcher',
		)
		self.handlers = TaskServer(
			master=self, 
			adapter=self.handle_adapter, 
			listener=conf.handle_conf['listener'], 
			password=conf.handle_conf['password'],
			log=self.log,
			name='handler',
		)
		self.counter = Counter(self)
		self.server = CountServer(self)

	def quit(self):
		self.log.info('%s - quiting ...' % self.name)
		self.fetchers.quit()
		self.handlers.quit()
		self.async.quit()
		self.sync.quit()
		self.counter.quit()

	def update(self):
		self.articles.update()

	def run(self):
		try:
			while not self.exited:
				self.update()
				self.sync.run()
				self.async.run()
				self.fetchers.run()
				self.handlers.run()
				self.server.run()
				self.counter.handle()
				self.wait(1)
		except KeyboardInterrupt:
			self.exit('KeyboardInterrupt')
		except Exception, e:
			import traceback
			traceback.print_exc(e)
			self.exit('Exception (%s) of Master: %s' % (e.__class__.__name__, str(e)))


def main():
	import conf
	import sys
	import logging

	if len(sys.argv) >= 2:
		level = logging.DEBUG
	else:
		level = logging.INFO

	log = logger('spider-master', level=level)
	master = Master(conf, log)
	master.run()


if __name__ == '__main__':
	main()