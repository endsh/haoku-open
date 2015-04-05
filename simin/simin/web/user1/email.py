# coding: utf-8
import os
import base64
import binascii
import hashlib
import urllib
from flask import current_app, render_template_string
from flask.ext.sendmail import Message
from simin.web.core import mail


access_email_html = u"""
<div>
	<p>尊敬的{{ username }}，您好：</p>
	<p>为了您的账户安全，请您点击下面的链接，进行邮箱验证：</p>
	<p><a href="{{ url }}" target="_blank">{{ url }}</a></p>
	<p>如果以上链接无法点击，请将上面的地址复制到您的浏览器(如ie/firefox/chrome)的地址栏打开。</p>
	<p>（注：此链接有效期为3天）</p>
</div>
"""

reset_pass_html = u"""
<div>
	<p>尊敬的{{ username }}，您好：</p>
	<p>您在好酷网申请找回密码，重设密码地址为：</p>
	<p><a href="{{ url }}" target="_blank">{{ url }}</a></p>
	<p>如果以上链接无法点击，请将上面的地址复制到您的浏览器(如ie/firefox/chrome)的地址栏打开。</p>
	<p>（注：此链接有效期为3天）</p>
</div>
"""


def create_access_token(email, t):
	key = hashlib.md5('%s|%f|%s' % (email, t, os.urandom(16).encode('hex'))).hexdigest()
	code = '%s|%f|%s' % (email, t, key)
	return key, base64.b64encode(code)


def decode_access_token(code):
	try:
		code = base64.b64decode(code)
		email, t, key = code.split('|')
		return email, float(t), key
	except (binascii.Error, ValueError), e:
		current_app.logger.error(str(e))


def send_access_email(user, code):
	msg = Message(u'好酷网 - 邮箱验证服务',
			sender=current_app.config.get('SERVICE_EMAIL'),
			recipients=[user.email],
			charset='utf-8')
	url = current_app.config.get('ACCESS_EMAIL_URL')
	params = urllib.urlencode({'code':code})
	url = '%s?%s' % (url, params)
	msg.html = render_template_string(access_email_html, 
		username=user.username, url=url)

	if current_app.status == 'DEBUG':
		current_app.logger.info(msg.html)
	elif current_app.status == 'TEST':
		current_app.logger.info(msg.html)
		mail.send(msg)
	else:
		mail.send(msg)


def send_reset_pass_email(user, code):
	msg = Message(u'好酷网 - 找回密码',
			sender=current_app.config.get('SERVICE_EMAIL'),
			recipients=[user.email],
			charset='utf-8')
	url = current_app.config.get('RESET_EMAIL_URL')
	params = urllib.urlencode({'code':code})
	url = '%s?%s' % (url, params)
	msg.html = render_template_string(reset_pass_html, 
		username=user.username, url=url)

	if current_app.status == 'DEBUG':
		current_app.logger.info(msg.html)
	elif current_app.status == 'TEST':
		current_app.logger.info(msg.html)
		mail.send(msg)
	else:
		mail.send(msg)