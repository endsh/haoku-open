# coding: utf-8
import threading
import thread
import inspect
import ctypes
import time
import traceback


def _async_raise(tid, exctype):
	if not inspect.isclass(exctype):
		raise TypeError('Only types can be raised (not instances)')
	res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
	if res == 0:
		raise ValueError('Invalid thread id')
	elif res != 1:
		ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
		raise SystemError('PyThreadState_SetAsyncExc failed')


class Thread(threading.Thread):

	def _get_tid(self):
		if not self.isAlive():
			raise threading.ThreadError('the thread is not active')

		if hasattr(self, '_thread_id'):
			return self._thread_id

		for tid, tobj in threading._active.items():
			if tobj is self:
				self._thread_id = ctypes.c_long(tid)
				return ctypes.c_long(tid)

		raise AssertionError("could not determine the thread's id")

	def raise_exc(self, exctype):
		_async_raise(self._get_tid(), exctype)

	def terminate(self):
		self.raise_exc(SystemExit)


class Worker(Thread):

	def __init__(self, name, master, log):
		super(Worker, self).__init__()
		self.name = name
		self.master = master
		self.log = log

	def run(self):
		self.log.info('worker %s is running ...' % self.name)
		try:
			while not self.master.exited:
				task = self.master.get()
				if not task:
					self.master.wait(0.5)
					continue
				self.master.do(task)
			self.log.info('worker %s is exit ...' % self.name)
		except KeyboardInterrupt:
			self.master.run_exit('worker %s keyboard interrupt')
		except SystemExit:
			self.log.info('worker %s is exit by SystemExit ...' % self.name)


class Master(object):

	def __init__(self, log, count=4):
		self.log = log
		self.count = count
		self.name = 'master'
		self.tasks = []
		self.results = []
		self.workers = {}
		self._exit = threading.Event()
		self._index = 0

	def index(self):
		self._index += 1
		return self._index

	def get(self):
		if len(self.tasks):
			return self.tasks.pop(0)

	def do(self, task):
		raise NotImplementedError

	def wait(self, timeout):
		self._exit.wait(timeout)

	@property
	def exited(self):
		return self._exit.is_set()

	def run_exit(self, msg):
		thread.start_new_thread(self.exit, msg)

	def kill(self):
		for name, worker in self.workers.items():
			if worker.isAlive():
				worker.terminate()
			del self.workers[name]
		self.log.info('kill all finish ...')

	def pre_exit(self):
		pass

	def on_exit(self):
		pass

	def exit(self, msg='unkonwn'):
		self.log.info('exit by reason: %s ...' % msg)
		self._exit.set()
		self.pre_exit()
		self.kill()
		self.on_exit()

	def clean(self):
		for name, worker in self.workers.items():
			if not worker.isAlive():
				del self.workers[name]
				self.log.info('worker %s is not alive, so clean now ...' 
					% worker.name)

		count = self.count - len(self.workers)
		if count:
			for i in xrange(count):
				name = '%s-%d' % (self.name, self.index())
				worker = Worker(name, self, self.log)
				worker.start()
				self.workers[name] = worker
			self.log.info('start %d new workers ...' % count)

	def load_tasks(self):
		raise NotImplementedError

	def finish_tasks(self):
		raise NotImplementedError

	def handle(self):
		self.load_tasks()
		self.finish_tasks()

	def run(self):
		self.log.info('master %s is running ...' % self.name)
		try:
			while not self.exited:
				self.clean()
				self.handle()
				self.wait(0.1)
		except KeyboardInterrupt:
			self.exit('keyboard interrupt')
		except Exception:
			self.log.info(traceback.format_exc())
			self.exit('error')
