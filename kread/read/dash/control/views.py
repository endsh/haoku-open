# coding: utf-8
from flask import Blueprint, render_template, request
from ..core import counter

bp = Blueprint('control', __name__)


@bp.route('/')
def control():
	return render_template('control/index.html')


@bp.route('/data')
def data():
	return counter.data()


@bp.route('/debug')
def debug():
	return render_template('control/debug.html')


@bp.route('/dump')
def dump():
	attrs = request.args.get('obj')
	if not attrs:
		return 'obj is null'

	return counter.dump(attrs)

@bp.route('/imgs')
def imgs():
	return counter.imgs()