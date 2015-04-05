# coding: utf-8
import os
import conf
import datetime
import logging
import redis


class RedisHandler(logging.Handler):
	""" redis log handler """

	def __init__(self, name, redis_conf):
		self.redis = redis.Redis(**redis_conf)
		self.index = 0
		self.timeout = 3
		self.prefix = 'log-' + name + '-'
		logging.Handler.__init__(self)

	def emit(self, record):
		msg = self.format(record)
		self.index += 1
		self.redis.setex(self.prefix + str(self.index), msg, self.timeout)


_filefmt = os.path.join(conf.logs_root,"%Y-%m-%d-%H.log")
class TimeHandler(logging.Handler):
	""" time log handler """

	def __init__(self, filefmt=_filefmt):
		""" init class """
		self.filefmt = filefmt
		logging.Handler.__init__(self)

	def emit(self, record):
		msg = self.format(record)
		_path = datetime.datetime.now().strftime(self.filefmt)
		_dir = os.path.dirname(_path)
		try:
			if os.path.exists(_dir) is False:
				os.makedirs(_dir)
		except Exception, e:
			print 'can not make dirs'
			print 'file path is', _path
			print str(e)
			pass

		try:
			fd = open(_path, 'a')
			fd.write(msg.encode('utf-8'))
			fd.write('\n')
			fd.flush()
			fd.close()
		except Exception, e:
			print 'can not write to file'
			print 'file path is', _path
			print str(e)


def logger(name, level=logging.INFO, stream=True, file=True, redis=False):
	""" logger handler """

	_log = logging.getLogger(name)
	_log.setLevel(level)
	
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

	if redis:
		_handler = RedisHandler(name, conf.redis_log)
		_handler.setLevel(level)
		_handler.setFormatter(formatter)
		_log.addHandler(_handler)

	if file:
		filefmt = os.path.join(conf.logs_root + os.sep + name, '%Y-%m-%d', '%H.log')
		_handler = TimeHandler(filefmt)
		_handler.setLevel(level)
		_handler.setFormatter(formatter)
		_log.addHandler(_handler)

	if stream:
		_handler = logging.StreamHandler()
		_handler.setLevel(level)
		_handler.setFormatter(formatter)
		_log.addHandler(_handler)

	return _log
