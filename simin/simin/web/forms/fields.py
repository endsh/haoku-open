# coding: utf-8
import time
import datetime
from flask import current_app
from wtforms import fields, widgets, validators
from wtforms.fields import Field, HiddenField, TextField
from .widgets import VerifyCode, UEditor
from ..verify import get_verify_code, on_validate_code


__all__ = [
	'VerifyCodeField', 'KDateField', 'KRadioField', 'UEditorField',
]

_unset_value = ''


class VerifyCodeField(Field):

	widget = VerifyCode()

	def __init__(self, label=None, key='verify_code', 
			hidden=False, invalid_times=2, **kwargs):
		super(VerifyCodeField, self).__init__(label, **kwargs)
		self.key = key
		self.invalid_times = invalid_times
		self.hidden = hidden
		self.code, self.times = get_verify_code(key)
		self._refresh = False

	def process_data(self, value):
		if self.hidden == True:
			self.data = self.code
		else:
			self.data = ''

	def process_formdata(self, valuelist):
		if not valuelist or not valuelist[0]:
			self.data = ''
		else:
			self.data = valuelist[0]

	def _value(self):
		return self.data

	def need_refresh(self):
		return self._refresh

	def validate(self, field, extra_validators=tuple()):
		self.errors = list(self.process_errors)
		if self.times >= self.invalid_times:
			self._refresh = True
			self.code, self.times = get_verify_code(self.key, refresh=True)
			self.errors.append(u'验证码已失效')
		if self.data.lower() != self.code.lower():
			on_validate_code(self.key)
			self.errors.append(u'验证码错误')
		return len(self.errors) == 0


class KListWidget(object):
	def __init__(self, html_tag='ul', sub_tag='li', sub_startswith='sub_', prefix_label=True):
		self.html_tag = html_tag
		self.sub_tag = sub_tag
		self.sub_startswith = sub_startswith
		self.prefix_label = prefix_label

	def __call__(self, field, **kwargs):
		kwargs.setdefault('id', field.id)
		sub_kwargs = dict((k[4:],v) for k, v in kwargs.iteritems() if k.startswith(self.sub_startswith))
		kwargs = dict(filter(lambda x: not x[0].startswith(self.sub_startswith), kwargs.iteritems()))
		sub_html = '%s %s' % (self.sub_tag, widgets.html_params(**sub_kwargs))
		html = ['<%s %s>' % (self.html_tag, widgets.html_params(**kwargs))]
		for subfield in field:
			if self.prefix_label:
				html.append('<%s>%s %s</%s>' % (sub_html, subfield.label, subfield(), self.sub_tag))
			else:
				html.append('<%s>%s %s</%s>' % (sub_html, subfield(), subfield.label, self.sub_tag))
		html.append('</%s>' % self.html_tag)
		return widgets.HTMLString(''.join(html))


class KRadioField(fields.SelectField):
	widget = KListWidget(html_tag='div', sub_tag='label', prefix_label=False)
	option_widget = widgets.RadioInput()


class KDateField(fields.DateTimeField):

	def __init__(self, label=None, validators=None, format='%Y-%m-%d', allow_null=False, **kwargs):
		super(KDateField, self).__init__(label, validators, format, **kwargs)
		self.allow_null = allow_null

	def _value(self):
		if self.raw_data:
			return ' '.join(self.raw_data)
		else:
			if self.data and type(self.data) in (str, unicode):
				return self.data
			return self.data and time.strftime(self.format, time.localtime(self.data)) or ''

	def process_formdata(self, valuelist):
		if valuelist:
			date_str = ' '.join(valuelist)
			if date_str:
				try:
					self.data = time.strptime(date_str, self.format)
				except ValueError:
					self.data = None
					raise ValueError(self.gettext('Invalid date/time input'))
			else:
				self.data = None
				if not self.allow_null:
					raise ValueError(self.gettext('Invalid date/time input'))


class UEditorField(fields.StringField):
	widget = UEditor()