# coding: utf-8
from jinja2 import Markup
from flask import current_app

__all__ = [
	'auto_markup', 'FilterManager',
]


def auto_markup(html):
	return Markup(html) if current_app.jinja_env.autoescape else html


class FilterManager(object):

	def __init__(self, app=None):
		if app is not None:
			self.init_app(app)

	def init_app(self, app):
		self.app = app
		filters = {
			'kform': self.kform_filter,
			'kform_inline': self.kform_inline_filter,
			'first_error': self.first_error_filter,
			'alert_first_error': self.alert_first_error_filter,
		}
		app.jinja_env.filters.update(filters)

	def kform_filter(form, label=4):
		label_class = 'control-label col-sm-%d' % label
		field_div = '<div class="col-sm-%d">' % (12 - label)
		out = []
		for field in form:
			if field.type != 'CSRFTokenField':
				out.append('<div class="form-group">')
				out.append(field.label(class_=label_class))
				out.append(field_div)
				if field.type == 'KRadioField':
					out.append(field(sub_class='radio-inline'))
				elif field.type == 'KCheckboxField':
					out.append(field(sub_class='checkbox-inline'))
				else:
					out.append(field(class_='form-control', data_label=field.label.text))
				out.append('</div></div>')
			else:
				out.append(field())
		return auto_markup(''.join(out))

	def kform_inline_filter(self, form):
		out = []
		for field in form:
			if field.type == 'BooleanField':
				out.append('<div class="checkbox"><label>%s %s</label></div>' 
					% (field(), field.label.text))
			elif field.type != 'CSRFTokenField':
				out.append(field(
					class_='form-control', 
					placeholder=field.label.text, 
					data_label=field.label.text))
			else:
				out.append(field())
		return auto_markup(''.join(out))

	def first_error_filter(self, form):
		for field in form:
			if field.errors:
				return field.errors[0]
		return ''

	def alert_first_error_filter(self, form, style='danger'):
		first_error = self.first_error_filter(form)
		if first_error:
			return auto_markup(
				'<div class="alert alert-%s"><button class="close" type="button" '
				'data-dismiss="alert" aria-hidden="true">&times;</button><span>'
				'%s</span></div>' % (style, first_error))
		return first_error