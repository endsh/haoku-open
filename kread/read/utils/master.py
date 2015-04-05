# coding: utf-8
import kson
import gevent
import gevent.server
import socket
import traceback

from utils import monkey, key2attr


class Worker(object):

	def __init__(self, conf, log):
		monkey.patch_socket()
		self.conf = conf
		self.log = log

	def connect(self):
		if not self.closed:
			self.log.warn('socket is connected.')
			return

		listener = self.conf['listener']
		password = self.conf['password']

		self.log.info('try to connect to master <%s:%d>' % listener)
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect(listener)
			sock.sendobj({'type':'password', 'password':password})
		except socket.error, e:
			self.log.warn('socket error on connect: %s' % str(e))
		else:
			self.socket = sock
			self.log.info('socket connect success.')

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

	def on_close(self):
		pass

	def close(self):
		self.log.info('closing ...')
		self.socket.close()
		del self.socket
		self.on_close()


class Master(object):

	def __init__(self, conf, log):
		monkey.patch_socket(patch_gevent=True)
		self.name = 'master'
		self.conf = conf
		self.log = log
		self._index = 0

	def index(self):
		self._index += 1
		return self._index

	def on_auth(self, message):
		return message.type == 'password' \
			and message.password == self.conf['password']

	def on_connect(self, socket, address, message):
		if not self.on_auth(message):
			return None

		index = self.index()
		name = '%s-%d' % (self.name, index)
		worker = {
			'address':address, 
			'name':name, 
			'index':index, 
			'socket':socket
		}
		self.workers[socket] = worker
		self.log.info('a new worker %s connected from address <%s:%d>.' 
			% (worker['name'], address[0], address[1]))
		return worker

	def on_load(self, worker, count):
		raise NotImplementedError

	def on_finish(self, worker, results):
		raise NotImplementedError

	def on_command(self, worker, args):
		raise NotImplementedError

	def on_message(self, worker, message):
		if message.type == 'load':
			return {'tasks':self.on_load(worker, message.count)}
		elif message.type == 'finish':
			self.on_finish(worker, message.results)
		elif message.type == 'command':
			self.on_command(worker, message.args)
		else:
			self.log.warn('unknown message type')

	def on_quit(self, socket):
		if socket in self.workers:
			self.log.info('worker %s quited.' % self.workers[socket]['name'])
			del self.workers[socket]
		else:
			self.log.info('worker with socket %s is not found on quit.' % str(socket))

	def serve_handler(self, socket, address):
		message = key2attr(socket.recvobj())
		worker = self.on_connect(socket, address, message)
		if not worker:
			return

		while True:
			try:
				obj = socket.recvobj()
				if obj == None:
					break
				res = self.on_message(worker, key2attr(obj))
				if res:
					socket.sendobj(res)
				gevent.sleep(0)
			except KeyError, e:
				self.log.warn('a KeyError from worker %s: %s' 
					% (worker['name'], str(e)))
				self.log.warn(traceback.format_exc())
				break

		self.on_quit(socket)

	def listen(self):
		try:
			self.workers = {}
			self.server = gevent.server.StreamServer(
				self.conf['listener'],
				self.serve_handler,
			)
			self._greenlet = gevent.spawn(self.server.serve_forever)
		except Exception, e:
			self.log.info('%s listen exception: %s' % (self.name, str(e)))

	def shutdown(self):
		if hasattr(self, 'server'):
			self.log.info('master %s shutdown ...' % self.name)
			self.server.stop()

	def listen_if_need(self):
		if not hasattr(self, 'server') or self.server.closed:
			self.shutdown()
			self.listen()

	def handle(self):
		self.log.info('master %s handle ...' % self.name)

	def run(self):
		self.log.info('master %s is running ...' % self.name)
		self.listen_if_need()
