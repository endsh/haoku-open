# coding: utf-8
from wtforms.compat import with_metaclass
from wtforms.form import FormMeta as WTFormMeta
from flask.ext.wtf import Form as WTForm


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
		return type.__call__(cls, *args, **kwargs)

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


class BaseFrom(with_metaclass(FormMeta, WTForm)):
	class Meta(object):
		locales = ('zh_CN', 'zh')


class Form(with_metaclass(FormMeta, WTForm)):
	class Meta(object):
		locales = ('zh_CN', 'zh')
