# coding: utf-8
from simin.web.forms import Form
from wtforms import fields


class CommentForm(Form):
	content = fields.TextAreaField(u'我来说两句...')