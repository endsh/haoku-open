# coding: utf-8
import json
import urllib
import urlparse
from flask import Blueprint, request, render_template, jsonify
from flask import current_app, redirect, url_for
from accounts.sdk.sso import current_user
from .forms import RegisterForm, LoginForm
from .forms import FindPassForm, ResetPassForm
from ..core import sso as sso_manager

bp = Blueprint('users', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if form.validate_on_submit():
		res = current_user.accounts.register(type='email', **form.data)
		return jsonify(res)
	elif form.is_submitted():
		res = dict(code=-1, msg=current_app.filter.first_error_filter(form))
		res['refresh'] = form.verify_code.need_refresh()
		return jsonify(res)
	return render_template('users/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
	next = request.args.get('next')
	if not next:
		next = url_for('profile.index')
	
	jsonp = ''
	res = urlparse.urlparse(next)
	if res.netloc:
		query = urllib.urlencode({'next':next.encode('utf-8')})
		jsonp = 'http://%s/jsonp?%s' % (res.netloc, query)

	form = LoginForm(request.form)
	if form.validate_on_submit():
		res = current_user.accounts.login(form.account.data, form.password.data)
		if res['code'] == 0:
			sso_manager.login(res['user'], res['token'], form.rememberme.data)
			return jsonify(dict(code=0))
		return jsonify(res)
	elif form.is_submitted():
		res = dict(code=-1, msg=current_app.filter.first_error_filter(form))
		res['refresh'] = form.verify_code.need_refresh()
		return jsonify(res)

	other = True if not current_user.login or request.args.get('other') == 'true' else False
	return render_template('users/login.html', form=form, jsonp=jsonp, next=next, other=other)


@bp.route('/check')
def check():
	res = current_user.accounts.check(**request.args)
	return jsonify(res)


@bp.route('/find_pass', methods=['GET', 'POST'])
def find_pass():
	form = FindPassForm(request.form)
	if form.validate_on_submit():
		res = current_user.accounts.find_pass(email=form.email.data)
		return jsonify(res)
	elif form.is_submitted():
		res = dict(code=-1, msg=current_app.filter.first_error_filter(form))
		res['refresh'] = form.verify_code.need_refresh()
		return jsonify(res)
	return render_template('users/find_pass.html', form=form)


@bp.route('/reset_pass', methods=['GET', 'POST'])
def reset_pass():
	form = ResetPassForm(request.form)
	code = request.args.get('code')
	if form.validate_on_submit():
		res = current_user.accounts.reset_pass(
			code=code,
			password=form.password.data,
			repassword=form.password.data,
		)
		return jsonify(res)
	elif form.is_submitted():
		res = dict(code=-1, msg=current_app.filter.first_error_filter(form))
		return jsonify(res)

	if code:
		res = current_user.accounts.reset_pass(code=code)
		if res['code'] == 0:
			return render_template('users/reset_pass.html', form=form, code=code)
		msg = res['msg']
	else:
		msg = u'链接无效'
	return render_template('error.html', msg=msg)


@bp.route('/logout')
def logout():
	next = url_for('.login')
	if not current_user.login:
		return redirect(next)

	res = current_user.accounts.logout()
	if res['code'] == 0:
		hosts = res['hosts']
	else:
		hosts = []

	sso_manager.logout()
	return render_template('users/logout.html', hosts=json.dumps(hosts), next=next)


@bp.route('/sso')
def sso():
	if current_user.login == True:
		res = current_user.accounts.ssotoken()
		return jsonify(res)
	return redirect(url_for('.login'))
