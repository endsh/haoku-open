# coding: utf-8
import time
from datetime import datetime
from flask import current_app, flash, redirect, render_template, request, url_for, abort
from flask.ext.login import login_required
from flask_login import current_user, login_user, logout_user
from .emails import send_reset_pass_email, create_access_token, decode_access_token, send_access_email
try: # Handle Python 2.x and Python 3.x
	from urllib.parse import quote	  # Python 3.x
except ImportError:
	from urllib import quote			# Python 2.x

@login_required
def change_password():
	um = current_app.kuser_manager
	form = um.change_password_form(request.form)

	if form.validate_on_submit():
		user = um.get_user_by_id(current_user.id)
		if not user:
			abort(400)
		if user.password == form.oldpassword.data:
			user.password = form.password.data
			user.update()
			return redirect(url_for(um.after_change_password_endpoint))
		else:
			flash('password error')
	return render_template(um.change_password_template, form=form)

@login_required
def change_username():
	um = current_app.kuser_manager
	form = um.change_username_form(request.form)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.update()
		return redirect(url_for(um.after_change_username_endpoint))

def login():
	um = current_app.kuser_manager
	next = request.args.get('next', um.after_login_endpoint)

	login_form = um.login_form(request.form)
	if login_form.validate_on_submit():
		user = um.find_user_by_username(login_form.username.data)
		if not user and um.enable_email:
			user = um.find_user_by_email(login_form.username.data)

		if user:
			return _do_login_user(user, next, login_form.rememberme.data)
		else:
			flash('Did your register?', 'error')
	# Process GET or invalid POST
	return render_template(um.login_template,
		form=login_form,
		login_form=login_form)


def register():
	kuser_manager =  current_app.kuser_manager
	next = request.args.get('next', kuser_manager.after_login_endpoint)

	# Initialize form
	register_form = kuser_manager.register_form(request.form)
	if register_form.validate_on_submit():
		fields = dict(

		)
		for field_name, field_value in register_form.data.items():
			if field_name == 'repassword':
				continue
			fields[field_name] = field_value
		user = kuser_manager.add_user(**fields)
		kuser_manager.commit()
		return redirect(url_for(kuser_manager.after_register_endpoint))

	return render_template(kuser_manager.register_template,
		form=register_form,
		register_form=register_form)

@login_required
def resend_confirm_email():
	um = current_app.kuser_manager
	form = um.resend_confirm_email_form(request.form)
	if form.validate_on_submit():
		user = um.find_user_by_email(form.email.data)
		if not user:
			flash('email is invalid', 'error')
		elif user.active:
			flask("email has been verify", 'error')
			return redirect(url_for(um.home_endpoint))
		user.access_token, code = create_access_token(user.email, time.time)
		user.update()
		send_access_email(user, code)
		return redirect(url_for(um.after_resend_confirm_email_endpoint))
	return render_template(um.resend_confirm_email_tempalte, form=form)

def confirm_email():
	um = current_app.kuser_manager
	code = request.args.get('code', '')
	try:
		email, t, key = decode_access_token(code)
	except Exception, e:
		print str(e)

	user = um.find_user_by_email(email)
	time_limit = um.email_token_time_limit
	if not user or key != user.access_token or time.time() - t > time_limit:
		return redirect(um.unauthenticated_endpoint)

	user.access_token = 'already_access'
	user.active = True
	user.update()
	return redirect(url_for(um.after_confirm_endpoint))


@login_required
def logout():
	logout_user()

	kuser_manager = current_app.kuser_manager
	next = request.args.get('next', url_for(kuser_manager.after_logout_endpoint))
	return redirect(next)

def forgot_password():
	um = current_app.kuser_manager
	form = um.forgot_password_form(request.form)
	if form.validate_on_submit():
		email = form.email.data
		user = um.find_user_by_email(email)
		if user is None:
			flash('check your email! this is invalid~', 'error')
			return redirect(url_for('.forgot_password'))
		elif not user.active:
			flash('please verify the email frist!', 'error')
			return redirect(url_for('.resend_confirm_email'))
		user.reset_token, code = create_access_token(user.email, time.time())
		user.update()
		send_reset_pass_email(user, code)
	return render_template(um.forgot_password_template, form=form)


@login_required
def user_profile():
	user_manager = current_app.kuser_manager
	return render_template(user_manager.user_profile_template)

def unauthenticated():
	url = request.url

	flash("You must be signed in to access '%s'." % url, 'error')

	quoted_url = quote(url)

	kuser_manager = current_app.kuser_manager
	
	return redirect(url_for(kuser_manager.unauthenticated_endpoint)+'?next='+ quoted_url)


def _do_login_user(user, next, rememberme):
	
	if not user: return unauthenticated()

	kuser_manager = current_app.kuser_manager
	if kuser_manager.enable_email and kuser_manager.enable_confirm_email \
			and not current_app.kuser_manager.enable_login_without_confirm_email:
		url = url_for('user.resend_confirm_email')
		flash('Your email address has not yet been confirmed. Check your email Inbox and Spam folders for the confirmation email or <a href="%(url)s">Re-send confirmation email</a>.' % url, 'error')
		return redirect(url_for(url))

	login_user(user, remember=rememberme)

	flash('You have signed in successfully.', 'success')

	return redirect(next)