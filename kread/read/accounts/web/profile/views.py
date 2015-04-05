# coding: utf-8
import hashlib
from flask import Blueprint, request, render_template
from flask import url_for, redirect, jsonify, current_app
from accounts.sdk.sso import current_user, login_required
from .forms import ProfileForm, AvatarForm, ChangePasswordForm
from ..core import AVATAR
bp = Blueprint('profile', __name__)


ALLOWED_FILE = set(['png', 'jpg', 'jpeg', 'gif', 'ico'])
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_FILE


@bp.route('')
@login_required
def index():
	res = current_user.accounts.profile(info=True)
	if res['code'] == 0:
		profile = ProfileForm(**res['profile'])
		user = res['info']
		profile = res['profile']
		if 'avatar' not in profile:
			profile['avatar'] = current_user.avatar
		profile_form = ProfileForm(**profile)
	else:
		user, profile = {}, {}
		profile_form = ProfileForm()

	avatar_form = AvatarForm()
	change_form = ChangePasswordForm()
	return render_template('profile/index.html', 
		user=user,
		profile=profile,
		profile_form=profile_form,
		avatar_form=avatar_form,
		change_form=change_form,
	)


@bp.route('/bind_email', methods=['GET', 'POST'])
def bind_email():
	if request.method == 'POST':
		if current_user.login:
			res = current_user.accounts.send_access_email()
		else:
			res = dict(code=-1, msg=u'请先登录')
		return jsonify(res)
	
	access = request.args.get('access')
	code = request.args.get('code')
	msg = ''
	if access == 'true' and code:
		res = current_user.accounts.bind_email(code)
		if res['code'] == 0:
			return redirect(url_for('.index'))
		msg = res['msg']
	elif not code:
		msg = u'无效链接'
	return render_template('profile/bind_email.html', access=access, code=code, msg=msg)


@bp.route('/avatar', methods=['POST'])
@login_required
def avatar():
	if current_user.login:
		file = request.files['avatar']
		if file and allowed_file(file.filename):
			_, _type = file.filename.rsplit('.', 1)
			filename = hashlib.md5('avatar_%d' % current_user.uid).hexdigest()
			path = AVATAR.put(filename, file.stream.read(), _type)
			res = current_user.accounts.avatar(avatar=path)
	else:
		res = dict(code=-1, msg=u'请先登录')
	return jsonify(res)


@bp.route('/save', methods=['POST', 'GET'])
@login_required
def save():
	form = ProfileForm(request.form)
	if form.validate_on_submit():
		res = current_user.accounts.save_profile(**form.data)
		return jsonify(res)
	res = dict(code=-1, msg=current_app.filter.first_error_filter(form))
	return jsonify(res)


@bp.route('/change', methods=['POST'])
@login_required
def change():
	form = ChangePasswordForm(request.form)
	if form.validate_on_submit():
		res = current_user.accounts.change_password(**form.data)
		return jsonify(res)

	res = dict(code=-1, msg=current_app.filter.first_error_filter(form))
	return jsonify(res)