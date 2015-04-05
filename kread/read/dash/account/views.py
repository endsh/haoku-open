# coding: utf-8
from flask import Blueprint, render_template, request
from flask import abort, redirect, current_app
from flask import url_for
from flask.ext.login import current_user, login_user, logout_user
from .forms import RegisterForm, LoginForm
from .models import Account
from ..core import json_success, json_error

bp = Blueprint('account', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
	if current_app.config.get('REGISTER_OPEN', False) == False:
		abort(404)

	form = RegisterForm()
	if form.validate_on_submit():
		user = form.save()
		return redirect(url_for('.login'))
	return render_template('account/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
	next_url = request.args.get('next', '/')
	if current_user.is_authenticated():
		return redirect(next_url)

	form = LoginForm()
	if form.validate_on_submit():
		user = form.get_user()
		login_user(user, form.rememberme.data)
		return redirect(next_url)
	return render_template('account/login.html', form=form)


@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('.login'))


@bp.route('/check_username')
def check_username():
	username = request.args.get('value', '')
	if username:
		if Account.query.filter_by(username=username).count() == 0:
			return json_success(exists=0)
		else:
			return json_success(exists=1)
	return json_error()


@bp.route('/check_email')
def check_email():
	email = request.args.get('value', '')
	if email:
		if Account.query.filter_by(email=email).count() == 0:
			return json_success(exists=0)
		else:
			return json_success(exists=1)
	return json_error()


@bp.route('/find')
def find():
	pass
