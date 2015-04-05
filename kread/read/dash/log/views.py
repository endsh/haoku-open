# coding: utf-8
from flask import Blueprint, render_template, request, jsonify
from ..core import mongo_admin
from ..account.models import Account
bp = Blueprint('log', __name__)


MONGO_TASK = mongo_admin.task
MONGO_RECODE = mongo_admin.recode

def test_jsonify(code):
	print code
	return jsonify(code)
	
@bp.route('/')
def index():
	tasks = MONGO_TASK.find()
	return render_template('log/index.html', tasks=list(tasks))


@bp.route('/userinfo', methods=['POST', 'GET'])
def userinfo():
	code = {'code':1}
	_id = request.args.get('_id', '')
	user_id = request.args.get('user_id', '')
	if not user_id or not _id:
		code['msg'] = 'user_id or _id is null'
		return test_jsonify(code)
	userinfo = Account.query.get(user_id)
	if not userinfo:
		code['msg'] = 'not user'
		return test_jsonify(code)

	code['code'] = 0
	recodes = MONGO_RECODE.find({'task_id': _id}, {'content':1, 'title':1, 'pubtime':1, '_id':0})

	if not recodes.count() :
		code['recode'] = 1
		return test_jsonify(code)
	code['recode'] = 0
	code['recodes'] = list(recodes)

	return test_jsonify(code)