# coding: utf-8
from flask import url_for
from wtforms.widgets import html_params, HTMLString
from cgi import escape
from wtforms.compat import text_type


class VerifyCode(object):

	html_params = staticmethod(html_params)

	def __call__(self, field, **kwargs):
		if field.hidden == True:
			html = '<input %s>' % self.html_params(
				id=field.id,
				type='hidden',
				name=field.name,
				value=field._value(),
			)
		else:
			html = '<div class="input-group input-group-lg">'
			html += '<input %s>' % self.html_params(
				id=field.id,
				type='text',
				name=field.name,
				value=field._value(),
				maxlength=4,
				**kwargs
			)
			html += '<span class="input-group-addon" style="padding:0px;"><img %s></span>' % self.html_params(
				id='%s_img' % field.id,
				src=url_for('verify_code', key=field.key),
				data_src=url_for('verify_code', key=field.key),
				style='cursor:pointer;',
				onclick="$(this).attr('src', '" + url_for('verify_code', key=field.key) + "&t=' + Math.random());"
			)
			html += '</div>'

		return HTMLString(html)


class UEditor(object):

	html_params = staticmethod(html_params)

	def __call__(self, field, **kwargs):
		kwargs.setdefault('id', field.id)
		kwargs.setdefault('type', 'text/plain')
		kwargs.setdefault('style', 'width:99%;height:360px;')
		kwargs['class'] = ''
		return HTMLString('<script %s>%s</script><script>var um = UM.getEditor("%s");</script>' % (html_params(name=field.name, **kwargs), text_type(field._value()), field.name))