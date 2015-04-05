# coding: utf-8
from flask import Blueprint, render_template

bp = Blueprint('about', __name__)


@bp.route('/')
def about():
	return render_template('about/about.html')

@bp.route('/join')
def join():
	return render_template('about/join.html')

@bp.route('/media')
def media():
	return render_template('about/media.html')

@bp.route('/link')
def link():
	return render_template('about/link.html')

@bp.route('/contact')
def contact():
	return render_template('about/contact.html')

@bp.route('/update')
def update():
	return render_template('about/update.html')