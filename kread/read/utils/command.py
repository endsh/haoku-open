# coding: utf-8


class Command(object):
	""" command utils """

	def __init__(self):
		""" init class """
		self.cmds = {}

	def run(self, cmd):
		""" run command """
		if cmd in self.cmds:
			self.cmds[cmd]()
		else:
			print cmd, 'not in command list'
			self.help()

	def help(self):
		""" print help """
		print 'Usage: haoku [cmd]'
		for key in sorted(self.cmds.keys()):
			print key

	def __call__(self, cmd=None):
		""" register command """
		def wrapper(func):
			self.cmds[cmd if cmd else func.__name__] = func
			return func
		return wrapper


cmd = Command()
