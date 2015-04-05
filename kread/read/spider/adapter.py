# coding: utf-8


class Adapter(object):

	def __init__(self, master, name):
		self.master = master
		self.log = master.log
		self.handles = []
		self.name = name

	def register(self, cmds, input, output, cancel, extend=False):
		self.handles.append({
			'cmds':cmds, 
			'input':input, 
			'output':output, 
			'cancel':cancel,
			'extend':extend,
		})

	def get(self, count, **kwargs):
		tasks = []
		for handle in self.handles:
			if not kwargs or handle['extend'] == True:
				tasks.extend(handle['input'](count - len(tasks), **kwargs))
			if len(tasks) >= count:
				break
		return tasks

	def cancel(self, key, cmd):
		for handle in self.handles:
			if cmd in handle['cmds']:
				handle['cancel'](key, cmd)
				break

	def finish(self, key, cmd, res):
		for handle in self.handles:
			if cmd in handle['cmds']:
				handle['output'](key, cmd, res)
				return