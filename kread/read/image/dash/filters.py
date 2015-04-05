# coding: utf-8
from jinja2 import Markup
from flask import current_app


_filters = {}

def register_filter(name):
	def wrapper(func):
		_filters[name] = func
		return func
	return wrapper


def init_app(app):
	global _filters
	for name, func in _filters.iteritems():
		app.jinja_env.filters[name] = func


def auto_markup(out):
	return Markup(out) if current_app.jinja_env.autoescape else out

@register_filter('kform')
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


@register_filter('kform_inline')
def kform_inline_filter(form):
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


@register_filter('first_error')
def first_error_filter(form):
	for field in form:
		if field.errors:
			return field.errors[0]
	return ''


@register_filter('alert_first_error')
def alert_first_error_filter(form, style='danger'):
	first_error = first_error_filter(form)
	if first_error:
		return auto_markup(
			'<div class="alert alert-%s"><button class="close" type="button" '
			'data-dismiss="alert" aria-hidden="true">&times;</button><span>'
			'%s</span></div>' % (style, first_error))
	return first_error
