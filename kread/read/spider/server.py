# coding: utf-8
import random
from Queue import Queue
from utils import make_worker
from spider.network import Server

BaseServer = make_worker(super_class=Server)


class TaskServer(BaseServer):

	def __init__(self, master, adapter, listener, password, log, timeout=0.5, name=None):
		super(TaskServer, self).__init__(
			instance=master,
			listener=listener,
			password=password,
			log=log,
			timeout=timeout,
			name=name,
		)
		self.master = master
		self.adapter = adapter
		self.keys = dict()
		self._busy = False

	@property
	def busy(self):
		size = self.master.async.size()

		# if size > 2000:
		# 	self.master.async.quick(100)
		# elif size > 500:
		# 	self.master.async.quick(50)
		# elif size > 200:
		# 	self.master.async.quick()

		if size > 10000:
			# self.master.async.quick(100)
			self._busy = True
			return True

		# if self._busy and size > 2000:
		# 	self.master.async.quick(100)
		# 	return True

		self._busy = False
		return False

	def on_connect(self, socket, address, message):
		worker = super(TaskServer, self).on_connect(socket, address, message)
		if not worker:
			return worker
		if 'seg' in message and message.seg == True:
			worker['seg'] = True
		else:
			worker['seg'] = False
		worker['keys'] = dict()
		return worker

	def on_load(self, worker, count):
		if self.busy:
			return []

		keys = worker['keys']

		if worker['seg'] == True:
			tasks = self.adapter.get(count, seg=True)
		else:
			tasks = self.adapter.get(count)

		for task in tasks:
			keys[task['key']] = task['cmd']
		self.log.debug('%s has %d/%d tasks on load.'
			% (worker['name'], len(tasks), count))
		return tasks

	def on_finish(self, worker, results):
		keys = worker['keys']
		for res in results:
			self.master.async.do(self.adapter.finish, res['key'], res['cmd'], res['res'])
			if res['key'] in keys:
				del keys[res['key']]

		self.log.debug('%s has %d tasks on finish.'
			% (worker['name'], len(results)))

	def on_close(self, socket):
		worker = super(TaskServer, self).on_close(socket)
		if worker:
			for key, cmd in worker['keys'].iteritems():
				self.keys[key] = cmd
			self.log.info('%s - cancel %d tasks on close.'
				% (worker['name'], len(worker['keys'])))
		return worker

	def finish(self, exit=False):
		while self.keys and not self.exited:
			key, cmd = self.keys.popitem()
			self.adapter.cancel(key, cmd)

	def handle(self):
		super(TaskServer, self).handle()
		self.finish()
		self.wait(self.timeout)

	def on_quit(self):
		self.finish(exit=True)
