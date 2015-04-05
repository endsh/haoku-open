# coding: utf-8
from flask import current_app, request, redirect, render_template
from flask import flash


def check_view():
	um = current_app.user_manager
	return um.check(request.args)


def login_view():
	um = current_app.user_manager
	next = request.args.get('next', um.login_next)
	if um.is_login():
		return redirect(next)
		
	form = um.login_form(request.form)
	if form.validate_on_submit():
		um.login_user(form)
		return redirect(next)
	return render_template(um.login_template, form=form)


def logout_view():
	um = current_app.user_manager
	next = request.args.get('next', um.logout_next)
	if um.is_login():
		um.logout_user()
	flash(u'退出成功。')
	return redirect(next)


def register_view():
	um = current_app.user_manager
	next = request.args.get('next', um.register_next)
	if um.is_login():
		return redirect(next)

	form = um.register_form(request.form)
	if form.validate_on_submit():
		um.register_user(form)
		flash(u'注册成功。')
		return redirect(next)
	return render_template(um.register_template, form=form)


def forget_password_view():
	um = current_app.user_manager
	next = request.args.get('next', um.forget_password_next)
	form = um.forget_password_form(request.form)
	if form.validate_on_submit():
		if um.forget_password(form):
			flash(u'密码重置邮件已发送，请稍后查收。')
			return redirect(next)
		else:
			flash(u'邮件发送失败。')
	return render_template(um.forget_password_template, form=form)


def reset_password_view():
	um = current_app.user_manager
	next = request.args.get('next', um.reset_password_next)
	code = request.args.get('code')
	

	form = um.reset_password_form(request.form)
	if form.validate_on_submit():
		um.reset_password(form)
		flash(u'密码重置成功。')
		return redirect(next)
	return render_template(um.reset_password_template, form=form)