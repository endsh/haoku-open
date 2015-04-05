# coding: utf-8
from __future__ import unicode_literals

from wtforms.compat import string_types, text_type


class Strip(object):

	def __call__(self, form, field):
		if isinstance(field.data, string_types):
			field.data = field.data.strip()


class Lower(object):

	def __call__(self, form, field):
		if isinstance(field.data, string_types):
			field.data = field.data.lower()


class Upper(object):

	def __call__(self, form, field):
		if isinstance(field.data, string_types):
			field.data = field.data.upper()


class Length(object):
	def __init__(self, min=-1, max=-1, message=None):
		assert min != -1 or max != -1, 'At least one of `min` or `max` must be specified.'
		assert max != -1 or min <= max, '`min` cannot be more than `max`.'
		self.min = min
		self.max = max
		self.message = message

	def __call__(self, form, field):
		l = field.data and len(field.data) or 0
		if l < self.min:
			message = self.message
			if message is None:
				message = '%(label)s长度不能小于%(min)d个字符'
			raise ValueError(message % dict(
				label=field.label.text, min=self.min, max=self.max, length=l))
		elif self.max != -1 and l > self.max:
			message = self.message
			if message is None:
				message = '%(label)s长度不能大于%(max)d个字符'
			raise ValueError(message % dict(
				label=field.label.text, min=self.min, max=self.max, length=l))


class DataRequired(object):

	field_flags = ('required', )

	def __init__(self, message=None):
		self.message = message

	def __call__(self, form, field):
		if not field.data or isinstance(field.data, string_types) and not field.data.strip():
			if self.message is None:
				message = '%(label)s不能为空'
			else:
				message = self.message
			raise ValueError(message % dict(label=field.label.text))
