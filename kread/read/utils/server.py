# coding: utf-8
import socket
import kson
kson.patch_socket()
import gevent
import gevent.monkey
import gevent.server
import utils
import logging

log = logging.getLogger('fetcher')

from kson import network
from gevent.socket import socket as gsocket
gsocket.recvbytes = network._recvbytes
gsocket.recvobj = network._recvobj
gsocket.sendobj = network._sendobj

gevent.monkey.patch_socket()


class Worker(object):

	def __init__(self, conf):
		self.conf = conf
		self.socket = self.connect(conf['listener'], conf['password'])

	def connect(self, listener, password):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(listener)
		sock.sendobj({'type':'password', 'password':password})
		return sock

	def sendobj(self, obj):
		return self.socket.sendobj(obj)

	def recvobj(self):
		return self.socket.recvobj()

	def close(self):
		self.socket.close()


class KServer(object):

	def __init__(self, conf):
		self.name = 'master'
		self.conf = conf
		self.server = gevent.server.StreamServer(
			self.conf['listener'], self.serve_handler)
		self.workers = {}
		self._greenlet = None
		self._index = 0

	def index(self):
		self._index += 1
		return self._index

	def on_password(self, message):
		return message.type == 'password' and message.password == self.conf['password']

	def on_connect(self, socket, address, message):
		if not self.on_password(message):
			return None
		index = self.index()
		name = '%s-%d' % (self.name, index)
		worker = {'address':address, 'name': name, 'index': index}
		self.workers[socket] = worker
		log.info('a new worker %s connected from address <%s:%d>.' 
			% (worker['name'], address[0], address[1]))
		return worker

	def on_load(self, worker, count):
		raise NotImplementedError

	def on_finish(self, worker, result):
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
			log.info('unknown message type')

	def on_quit(self, socket):
		if socket in self.workers:
			log.info('worker %s quited.' % self.workers[socket]['name'])
			del self.workers[socket]
		else:
			log.info('worker with socket %s is not found on quit.' % str(socket))

	def serve_handler(self, socket, address):
		message = utils.key2attr(socket.recvobj())
		worker = self.on_connect(socket, address, message)
		if not worker:
			return

		while True:
			try:
				obj = socket.recvobj()
				if obj == None:
					break
				res = self.on_message(worker, utils.key2attr(obj))
				if res:
					socket.sendobj(res)
			except KeyError, e:
				log.warn('a KeyError from worker %s: %s' % (worker['name'], str(e)))

		self.on_quit(socket)

	def handle(self):
		log.info('master %s handle.' % self.name)

	def run(self):
		self._greenlet = gevent.spawn(self.server.serve_forever)
		log.info('master %s is running.' % self.name)
