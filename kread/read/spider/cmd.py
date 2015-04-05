# coding: utf-8


class Command(object):
	""" command utils """

	def __init__(self):
		""" init class """
		self.cmds = {}

	def run(self, cmd, *args, **kwargs):
		""" run command """
		if cmd in self.cmds:
			return self.cmds[cmd](*args, **kwargs)
		else:
			raise KeyError('%s not in command list' % cmd)

	def __call__(self, cmd=None):
		""" register command """
		def wrapper(func):
			self.cmds[cmd if cmd else func.__name__] = func
			return func
		return wrapper


handle = Command()
