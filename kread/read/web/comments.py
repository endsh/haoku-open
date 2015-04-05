# coding: utf-8
from flask import Blueprint, render_template

bp = Blueprint('commments', __name__)


@bp.route('/')
def about():
	return render_template('home/comments.html')