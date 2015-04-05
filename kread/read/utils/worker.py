# coding: utf-8
import sys
import gevent
import gevent.event
import gevent.pool
import signal
import logging
import traceback

__all__ = [
	'BaseWorker', 'SimpleWorker', 'GroupWorker',
	'make_worker', 'make_group', 'new_worker',
	'simple_worker', 'group_worker', 'do',
	'Worker', 'Group',
]


class GreenletStop(Exception):
	pass


class BaseWorker(object):

	def __init__(self, log=None, term=False, name=None):
		self.log = log if log is not None else logging.getLogger()
		self.name = name if name is not None else self.__class__.__name__
		self.event = gevent.event.Event()
		if term is True:
			gevent.signal(signal.SIGTERM, self.term)

	def wait(self, timeout=0):
		# self.event.wait(timeout)
		gevent.sleep(timeout)

	def set(self):
		self.event.set()

	def go2exit(self, msg=''):
		gevent.spawn(self.exit, msg)

	@property
	def exited(self):
		return self.event.is_set()

	def exit(self, msg=''):
		self.set()
		self.quit()

	def quit(self):
		self.log.info('%s - quit ...' % self.name)

	def on_quit(self):
		self.log.info('%s - on quiting ...' % self.name)

	def term(self):
		self.exit('signal term.')


class SimpleWorker(BaseWorker):

	def __init__(self, log=None, timeout=0.5, name=None):
		super(SimpleWorker, self).__init__(log=log, name=name)
		self.timeout = timeout
		self.greenlet = None

	def handle(self):
		raise NotImplementedError

	def loop(self):
		while not self.exited:
			self.handle()
			self.wait(self.timeout)

	def _loop(self):
		try:
			self.loop()
		except KeyboardInterrupt:
			self.log.info('KeyboardInterrupt of %s' % self.name)
			self.exit('KeyboardInterrupt of %s' % self.name)
		except Exception, e:
			self.log.warn('exception of %s: %s' % (self.name, str(e)))
			self.log.warn(traceback.format_exc(limit=50))

	def join(self):
		if self.alive:
			self.greenlet.join()

	def kill(self):
		if self.alive:
			self.greenlet.kill(block=False, timeout=0.2)

	def quit(self):
		self.log.info('%s - quiting ...' % self.name)
		self.kill()
		self.on_quit()	

	@property
	def alive(self):
		return self.greenlet and not self.greenlet.dead

	def run(self):
		if not self.exited and not self.alive:
			self.greenlet = gevent.spawn(self._loop)

	def forever(self):
		self._loop()


class GroupWorker(SimpleWorker):

	def __init__(self, log=None, count=10, timeout=0.5, name=None):
		super(GroupWorker, self).__init__(log=log, timeout=0.5, name=name)
		self.count = count
		self.pool = gevent.pool.Pool(count)

	@property
	def free(self):
		return self.pool.free_count()

	@property
	def active(self):
		return self.count - self.free

	def handle(self):
		raise NotImplementedError

	def spawn(self):
		for _ in xrange(min(self.free, self.count)):
			self.pool.spawn(self.handle)

	def clean(self):
		for greenlet in list(self.pool):
			if greenlet.dead:
				self.pool.discard(greenlet)

	def quit(self):
		self.kill()
		self.pool.kill(block=False)
		self.on_quit()

	def loop(self):
		while not self.exited:
			self.clean()
			self.spawn()
			self.wait(self.timeout)


def make_worker(super_class=SimpleWorker, loop=None, handle=None):

	class Worker(super_class):

		def __init__(self, instance, *args, **kwargs):
			super(Worker, self).__init__(*args, **kwargs)
			if hasattr(instance, 'wait'):
				self.wait = instance.wait
			if hasattr(instance, 'exit'):
				self.exit = instance.exit
			if hasattr(instance, 'exited'):
				self.__dict__['exited'] = property(lambda: instance.exited)

	if loop is not None:
		Worker.loop = loop
	if handle is not None:
		Worker.handle = handle

	return Worker


def make_group(loop=None, handle=None):
	return make_worker(super_class=GroupWorker, loop=loop, handle=handle)


def new_worker(instance, super_class=SimpleWorker, loop=None, handle=None, *args, **kwargs):
	worker = make_worker(super_class=super_class, loop=loop, handle=handle)
	return worker(instance, *args, **kwargs)


def simple_worker(instance, loop=None, handle=None, *args, **kwargs):
	return new_worker(instance, loop=loop, handle=handle, *args, **kwargs)


def group_worker(instance, loop=None, handle=None, *args, **kwargs):
	return new_worker(instance, super_class=GroupWorker, loop=loop, handle=handle, *args, **kwargs)


def do(tasks, handle, count=10, timeout=0.1):
	results = []

	class TaskWorker(GroupWorker):

		def handle(self):
			while tasks:
				task = tasks.pop()
				results.append((task, handle(task)))

		@property
		def exited(self):
			return not tasks

	TaskWorker().forever()
	
	return results


Worker = make_worker()
Group = make_group()