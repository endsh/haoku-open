# coding: utf-8
from datetime import datetime, timedelta
from flask import request
from wtforms.compat import with_metaclass
from wtforms.form import Form as WTForm
from wtforms.form import FormMeta as WTFormMeta
from .fields import VerifyCodeField

__all__ = [
	'FormMeta', 'BaseForm', 'Form',
]


class FormMeta(WTFormMeta):

	def __init__(cls, name, bases, attrs):
		type.__init__(cls, name, bases, attrs)
		cls._unbound_fields = None
		cls._wtforms_meta = None

	def __call__(cls, *args, **kwargs):
		if cls._unbound_fields is None:
			fields = []
			for name in dir(cls):
				if not name.startswith('_') or name == '_id':
					unbound_field = getattr(cls, name)
					if hasattr(unbound_field, '_formfield'):
						fields.append((name, unbound_field))

			fields.sort(key=lambda x: (x[1].creation_counter, x[0]))
			cls._unbound_fields = fields

		if cls._wtforms_meta is None:
			bases = []
			for mro_class in cls.__mro__:
				if 'Meta' in mro_class.__dict__:
					bases.append(mro_class.Meta)
			cls._wtforms_meta = type('Meta', tuple(bases), {})

		res = type.__call__(cls, *args, **kwargs)
		for name, unbound_field in cls._unbound_fields:
			if hasattr(unbound_field, 'addon'):
				setattr(getattr(res, name), 'addon', getattr(unbound_field, 'addon'))
		return res

	def __setattr__(cls, name, value):
		if name == 'Meta':
			cls._wtforms_meta = None
		elif (not name.startswith('_') or name == '_id') and hasattr(value, '_formfield'):
			cls._unbound_fields = None
		type.__setattr__(cls, name, value)

	def __delattr__(cls, name):
		if not name.startswith('_') or name == '_id':
			cls._unbound_fields = None
		type.__delattr__(cls, name)


class BaseForm(with_metaclass(FormMeta, WTForm)):
	class Meta(object):
		locales = ('zh_CN', 'zh')

	def is_submitted(self):
		return request and request.method in ('PUT', 'POST')

	def validate_on_submit(self):
		return self.is_submitted() and self.validate()


class Form(with_metaclass(FormMeta, WTForm)):
	class Meta(object):
		locales = ('zh_CN', 'zh')

	def is_submitted(self):
		return request and request.method in ('PUT', 'POST')

	def validate_on_submit(self):
		return self.is_submitted() and self.validate()
