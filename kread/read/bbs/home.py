# coding: utf-8
from flask import Blueprint, request, render_template, jsonify
from flask import current_app, redirect, url_for
from accounts.sdk.sso import current_user, login_required

bp = Blueprint('home', __name__)


@bp.route('')
def index():
	print current_user.__dict__
	return str(current_user.login)


@bp.route('/profile')
@login_required
def profile():
	return str(current_user.login) 
