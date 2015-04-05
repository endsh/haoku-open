# coding: utf-8
from __future__ import unicode_literals
from wtforms.fields import SelectField, DateTimeField
from wtforms.widgets import RadioInput, HTMLString, html_params
import datetime


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
		sub_html = '%s %s' % (self.sub_tag, html_params(**sub_kwargs))
		html = ['<%s %s>' % (self.html_tag, html_params(**kwargs))]
		for subfield in field:
			if self.prefix_label:
				html.append('<%s>%s %s</%s>' % (sub_html, subfield.label, subfield(), self.sub_tag))
			else:
				html.append('<%s>%s %s</%s>' % (sub_html, subfield(), subfield.label, self.sub_tag))
		html.append('</%s>' % self.html_tag)
		return HTMLString(''.join(html))


class KRadioField(SelectField):
	widget = KListWidget(html_tag='div', sub_tag='label', prefix_label=False)
	option_widget = RadioInput()


class KDateField(DateTimeField):

	def __init__(self, label=None, validators=None, format='%Y-%m-%d', allow_null=False, **kwargs):
		super(KDateField, self).__init__(label, validators, format, **kwargs)
		self.allow_null = allow_null

	def process_formdata(self, valuelist):
		if valuelist:
			date_str = ' '.join(valuelist)
			if date_str:
				try:
					self.data = datetime.datetime.strptime(date_str, self.format).date()
				except ValueError:
					self.data = None
					raise ValueError('日期/时间 格式不正确')
			else:
				self.data = None
				if not self.allow_null:
					raise ValueError('日期/时间 格式不正确')