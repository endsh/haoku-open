# coding: utf-8
import sys
import kson
import gevent
import gevent.server
import socket
import traceback

from utils import monkey, key2attr
from utils import SimpleWorker, simple_worker


class Client(object):

	def __init__(self, listener, password, log, patch_gevent=False):
		self.listener = listener
		self.password = password
		self.log = log
		self.name = 'uname'
		monkey.patch_socket(patch_gevent)

	def connect(self, **kwargs):
		if not self.closed:
			self.log.warn('socket is connected.')
			return

		self.log.info('try to connect to master <%s:%d>' % self.listener)
		try:
			message = {'type':'password', 'password':self.password}
			message.update(kwargs)
			
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect(self.listener)
			sock.sendobj(message)
			self.socket = sock
			message = self.recvobj()
			if message['code'] == 'success':
				self.name = message['name']
			else:
				self.name = 'uname'
		except socket.error, e:
			self.log.warn('socket error on connect: %s' % str(e))
		else:
			self.log.info('socket of %s connect success.' % self.name)

	def sendobj(self, obj):
		self.socket.sendobj(obj)

	def recvobj(self):
		message = self.socket.recvobj()
		if not message:
			raise socket.error('recvobj return None')
		return message

	@property
	def closed(self):
		return not hasattr(self, 'socket')

	def close(self):
		self.log.info('%s closing ...' % self.name)
		
		socket = self.__dict__.pop('socket', None)
		if socket is not None:
			socket.close()

		self.on_close()
		self.name = 'uname'

	def on_close(self):
		pass


class Server(SimpleWorker):

	def __init__(self, listener, password, log, timeout=0.1, name=None):
		super(Server, self).__init__(log, timeout=0.1, name=name)
		self.listener = listener
		self.password = password
		monkey.patch_socket(patch_gevent=True)
		self.server_worker = simple_worker(self, loop=self.server_loop)
	
	@property
	def index(self):
		if not hasattr(self, '_index'):
			self._index = 0
		self._index += 1
		return self._index

	def on_auth(self, message):
		return message.type == 'password' \
			and message.password == self.password
	def on_connect(self, socket, address, message):
		if not self.on_auth(message):
			return None

		index = self.index
		name = '%s-%d' % (self.name, index)
		worker = {
			'address':address,
			'name':name,
			'index':index,
			'socket':socket,
		}
		self.workers[socket] = worker
		socket.sendobj({'code':'success', 'name':name})
		self.log.info('%s - a new worker %s connected from address: <%s:%d>'
			% (self.name, worker['name'], address[0], address[1]))
		return worker

	def on_load(self, worker, count):
		raise NotImplementedError

	def on_finish(self, worker, results):
		raise NotImplementedError

	def on_message(self, worker, message):
		if message.type == 'load':
			return {'tasks':self.on_load(worker, message.count)}
		elif message.type == 'finish':
			self.on_finish(worker, message.results)
		else:
			self.log.warn('%s - unkonwn message type: %s' % message.type)

	def on_close(self, socket):
		worker = self.workers.pop(socket, None)
		if worker:
			self.log.info('%s - %s closed.' % (self.name, worker['name']))
		else:
			host, port = socket.getsockname()
			self.log.info('%s - socket <%s:%d> closed.' % (self.name, host, port))
		return worker

	def handle_worker(self, socket, address):
		try:
			message = key2attr(socket.recvobj())
			worker = self.on_connect(socket, address, message)
			if not worker:
				return

			while not self.exited:
				try:
					obj = socket.recvobj()
					if obj == None:
						break
					res = self.on_message(worker, key2attr(obj))
					if res:
						socket.sendobj(res)
					self.wait()
				except KeyError, e:
					self.log.warn('%s - KeyError from %s: %s'
						% (worker['name'], str(e)))
					break
		except KeyboardInterrupt:
			self.exit('KeyboardInterrupt of %s' % self.name)
		except Exception, e:
			self.log.warn('%s - except %s: %s' 
				% (self.name, e.__class__.__name__, str(e)))
			self.log.debug(traceback.format_exc(limit=50))
		self.on_close(socket)

	def server_loop(self):
		try:
			self.workers = {}
			self.server = gevent.server.StreamServer(
				self.listener, self.handle_worker)
			self.log.info('%s - now runing ...' % self.name)
			self.server.serve_forever(stop_timeout=1)
		except KeyboardInterrupt:
			self.exit('KeyboardInterrupt of %s' % self.name)
		except Exception, e:
			self.log.warn('%s - except %s: %s' 
				% (self.name, e.__class__.__name__, str(e)))
			self.log.debug(traceback.format_exc(limit=50))
			self.exit('%s - %s' % (self.name, str(e)))

	def shutdown(self):
		if hasattr(self, 'server'):
			self.log.info('%s - shutdown ...' % self.name)
			self.server.stop()
			self.server_worker.quit()
			self.__dict__.pop('server', None)

	def quit(self):
		self.log.debug('%s - quiting ...' % self.name)
		self.kill()
		self.shutdown()
		self.on_quit()

	def handle(self):
		if not hasattr(self, 'server'):
			self.server_worker.run()
