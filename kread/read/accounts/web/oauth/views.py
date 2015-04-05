# coding: utf-8
from flask import Blueprint, request

bp = Blueprint('oauth', __name__)


@bp.route('/connect')
def connect():
	return '''<!DOCTYPE html>
	<html>
	<head>
	<script type="text/javascript"
src="http://qzonestyle.gtimg.cn/qzone/openapi/qc_loader.js" charset="utf-8" data-callback="true"></script>
	</head>
	</html>
'''