# coding: utf-8
import datetime
from flask import session, current_app
from flask.ext.wtf import Form as WTForm


class BaseFrom(WTForm):
	class Meta:
		locales = ('zh_CN', 'zh')


class Form(WTForm):
	class Meta:
		locales = ('zh_CN', 'zh')
