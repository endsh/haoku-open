# coding: utf8
import kson


def patch_socket(patch_gevent=False):
	""" patch socket """

	kson.patch_socket()

	if patch_gevent:
		from gevent import monkey
		monkey.patch_socket()

		from kson import network
		from gevent.socket import socket

		socket.recvbytes = network._recvbytes
		socket.recvobj = network._gzip_recvobj
		socket.sendobj = network._gzip_sendobj
