# coding: utf-8
import sys
import socket
import gevent
from gevent import Timeout, GreenletExit
from gevent.queue import Queue
from db import MongoIWeb
from utils import get, url2filetype
from utils.worker import GroupWorker, simple_worker, GreenletStop
from spider.network import Client


class Fetcher(GroupWorker, Client):

	def __init__(self, conf, log, timeout=0.5, waitout=0.1):
		GroupWorker.__init__(self, log=log, count=conf['count'], timeout=timeout, name='fetcher')
		Client.__init__(self, conf['listener'], conf['password'], log, patch_gevent=True)
		self.mongo = MongoIWeb(conf['mongo_iweb'])
		self.html_file = self.mongo.html_file
		self.image_file = self.mongo.image_file
		self.tasks = Queue()
		self.results = Queue()
		self.round = conf['round']
		self.waitout = waitout
		self.sync = simple_worker(self, loop=self.sync_loop)
		self.name = 'fetcher'

	def put(self, res):
		if not self.exited and not self.closed:
			self.results.put(res)

	def do(self, task):
		key, cmd, info = task['key'], task['cmd'], task['info']
		url = info['url']

		res = {}
		try:
			with Timeout(600) as timeout:
				headers = {}
				if 'src' in task:
					headers['Referer'] = task['src']
				try:
					if cmd == 'img':
						res['html'] = get(url, headers=headers, 
							allow_types=['*/*'], stream=True, max_len=2*1024*1024)
						res['path'] = self.image_file.put(key, res['html'], url2filetype(url))
						if not res['path']:
							raise ValueError('put html failed.')
					else:
						res['html'] = get(url, max_len=2*1024*1024)
						if cmd == 'art' or cmd == 'page':
							res['path'] = self.html_file.put(key, res['html'], 'html')
							if not res['path']:
								raise ValueError('put html failed.')
				except ValueError, e:
					self.log.warn('get %s: %s' % (url, str(e)))
					res['exc'] = e.__class__.__name__
				else:
					self.log.debug('fetch %-4s - success: %s' % (cmd, url))
					self.put({'key':key, 'cmd': cmd, 'res':res})
					return
		except Timeout:
			self.log.warn('%s timeout ...' % url)
			res['exc'] = 'Timeout'
		except GreenletExit:
			self.log.info('%s kill with GreenletExit ...' % url)
			return
		except KeyboardInterrupt:
			self.exit('KeyboardInterrupt of %s' % url)
			return
		except Exception, e:
			res['exc'] = e.__class__.__name__
			self.log.warn('except from %s: %s' % (url, str(e)))

		self.put({'key':key, 'cmd':cmd, 'res':res})

	def handle(self):
		while not self.closed and not self.tasks.empty():
			self.do(self.tasks.get())

	def load(self):
		if self.tasks.qsize() < 200:
			self.sendobj({'type':'load', 'count':self.round})
			message = self.recvobj()
			for task in message['tasks']:
				self.tasks.put(task)
			if not message['tasks']:
				self.finish()
				self.wait(1)
			self.log.info('load %d tasks.' % len(message['tasks']))

	def finish(self):
		results = []
		for _ in xrange(min(100, self.results.qsize())):
			results.append(self.results.get())
		if results:
			self.sendobj({'type':'finish', 'results':results})
			self.log.info('finish %d tasks.' % len(results))

	def sync_loop(self):
		self.log.info('sync handle start ...')
		try:
			while not self.exited:
				self.load()
				self.finish()
				self.wait(self.timeout)
		except socket.error, e:
			self.log.warn('sync handle socket error: %s' % str(e))
			self.close()

	def connect_if_need(self):
		timeout = 0
		while self.closed and not self.exited:
			self.wait(timeout)
			self.connect()
			if timeout < 5:
				timeout += 1

	def on_close(self):
		self.pool.kill()
		self.wait(2)
		self.tasks = Queue()
		self.results = Queue()

	def loop(self):
		while not self.exited:
			self.clean()
			self.spawn()
			self.connect_if_need()
			self.sync.run()
			self.wait(self.timeout)


def main():
	import conf
	import logging

	if len(sys.argv) >= 2:
		level = logging.DEBUG
	else:
		level = logging.INFO

	log = logging.getLogger(__name__)
	log.setLevel(level)
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
	_handler = logging.StreamHandler()
	_handler.setLevel(level)
	_handler.setFormatter(formatter)
	log.addHandler(_handler)

	fetcher_conf = {
		'listener':conf.fetch_conf['listener'],
		'password':conf.fetch_conf['password'],
		'mongo_iweb': conf.mongo_iweb,
		'count':20,
		'round':200,
	}
	fetcher = Fetcher(fetcher_conf, log)
	fetcher.forever()


if __name__ == '__main__':
	main()