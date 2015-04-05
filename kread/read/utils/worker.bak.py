# coding: utf-8
import signal
import gevent
from gevent import pool, monkey, Timeout
from .command import cmd as command

__all__ = [
	"SimpleWorker", "BaseGeventWorker", "GeventWorker", "KGreenletExit", 
	"do", "working", "auto_work",
]


class SimpleWorker(object):
	""" common worker """

	def __init__(self):
		""" init class """
		self._exit = False
		signal.signal(signal.SIGTERM, self.quit)

	def init_tasks(self, tasks):
		""" init tasks """
		self.tasks = tasks

	def run(self, tasks=None, handle=None):
		""" start work """
		if not tasks:
			tasks = self.tasks

		if not handle:
			handle = self.handle

		try:
			for index, task in enumerate(tasks):
				handle(index, task)
				if self.exited:
					break
		except KeyboardInterrupt, e:
			self.exit()
			return
		self.on_exit()

	def handle(self, index, task):
		""" handle task """
		pass

	def exit(self):
		""" exit work """
		self._exit = True
		self.on_exit()

	def on_exit(self):
		""" on exit """
		pass

	@property
	def exited(self):
		return self._exit

	def quit(self):
		""" quit on kill """
		self.exit()


class KGreenletExit(Exception):
	""" custom greenlet exit exception """
	pass


class BaseGeventWorker(object):
	""" base gevent worker """

	def __init__(self):
		monkey.patch_socket()
		self._event = gevent.event.Event()
		gevent.signal(signal.SIGTERM, self.quit)

	def wait(self, timeout):
		self._event.wait(timeout)

	def set_exit_event(self):
		self._event.set()

	def do_exit(self, msg=''):
		gevent.spawn(self.exit, msg)

	def exit(self, msg=''):
		self.set_exit_event()
		self.on_exit(msg=msg)

	def on_exit(self, msg=''):
		pass

	@property
	def exited(self):
		return self._event.is_set()

	def quit(self):
		self.exit('signal quit')


class GeventWorker(object):
	""" common gevent worker """

	def __init__(self, count=10):
		""" init class """
		monkey.patch_socket()
		self._index = 0
		self._count = count
		self._pool = pool.Pool(self._count)
		self._event = gevent.event.Event()
		gevent.signal(signal.SIGTERM, self.quit)

	def init_tasks(self, tasks):
		""" init tasks """
		self.tasks = tasks

	def index(self):
		""" index counter """
		return self._index

	def count(self):
		""" worker count """
		return self._count

	def free_count(self):
		return self._pool.free_count()

	def run(self, tasks=None, handle=None):
		""" start work """
		if not tasks:
			tasks = self.tasks

		if not handle:
			handle = self.handle

		try:
			for task in tasks:
				self.do(task, handle)
				if self.exited:
					break
				if self._index % int(self._count / 2) == 0:
					self.clean()
			self._pool.join()
		except KeyboardInterrupt, e:
			self.exit()
			return
		self.on_exit()

	def do(self, task, handle=None):
		""" do task """
		if not handle:
			handle = self.handle
		self._pool.spawn(handle, self._index, task)
		self._index += 1

	def handle(self, index, task):
		""" handle task """
		pass

	def clean(self):
		""" clean dead greenlet """
		for greenlet in list(self._pool):
			if greenlet.dead:
				self._pool.discard(greenlet)

	def wait(self, timeout):
		self._event.wait(timeout)

	@property
	def exited(self):
		return self._event.is_set()

	def do_exit(self, msg=''):
		gevent.spawn(self.exit, msg)

	def exit(self, msg=''):
		""" exit work """
		self._event.set()
		self._pool.kill()
		self._pool.join(timeout=Timeout(3))
		self._pool.kill()
		self.on_exit(msg=msg)

	def on_exit(self, msg=''):
		""" on exit """
		pass

	def quit(self):
		""" quit on kill """
		self.exit('signal quit')


def do(tasks, handle, worker=GeventWorker, count=10):
	results = []
	def new_handle(index, task):
		results.append((task, handle(task)))

	work = worker(count) if isinstance(worker, GeventWorker) else worker()
	work.run(tasks, new_handle)

	return results


def working(tasks, cmd=None, worker=SimpleWorker, count=10):
	def wrapper(handle):
		@command(cmd or handle.__name___)
		def new_handle():
			work = worker(count) if isinstance(worker, GeventWorker) else worker()
			work.run(tasks, handle)
		return new_handle
	return wrapper


def auto_work(cmd=None, *args, **kwargs):
	def wrapper(cls):
		@command(cmd or cls.__name___)
		def new_handle():
			work = cls(*args, **kwargs)
			work.run()
		return cls
	return wrapper
	