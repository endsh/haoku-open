# coding: utf-8
from flask import Blueprint, request, render_template, send_from_directory
from flask import redirect, url_for
from .forms import DomainForm, CatecoryForm, AlbumForm
from .models import Domain, Catecory, Album
import json, os
import conf
bp = Blueprint('getter', __name__)

@bp.route('/img/<path:img>')
def getimg(img):
	return send_from_directory(conf.data_root + os.sep + 'img', img)


@bp.route('/')
@bp.route('/domain')
@bp.route('/domain/<int:page>')
def domain(page=1):
	pagination = Domain.objects.paginate(page=page, per_page=20)
	return render_template(
		'getter/domain.html', 
		pagination=pagination, 
		endpoint='getter.domain')


@bp.route('/domain/add', methods=['GET', 'POST'])
@bp.route('/domain/edit/<id>', methods=['GET', 'POST'])
def edit_domain(id=None):
	if id:
		domain = Domain.objects.get_or_404(pk=id)
		form = DomainForm(request.form, obj=domain)
	else:
		domain = Domain()
		form = DomainForm(request.form)
	if form.validate_on_submit():
		form.populate_obj(domain)
		domain.save()
		return redirect(url_for('getter.domain'))
	return render_template('getter/edit_domain.html', form=form)


@bp.route('/domain/<id>/status/<regex("valid|invalid"):status>')
def domain_status(id, status):
	domain = Domain.objects.get_or_404(pk=id)
	domain.status = status
	domain.save()
	next_url = url_for('getter.domain')
	if request.args.get('next'):
		next_url = request.args.get('next')
	return redirect(next_url)


@bp.route('/domain/<id>/delete')
def delete_domain(id):
	domain = Domain.objects.get_or_404(pk=id)
	domain.delete()
	next_url = url_for('getter.domain')
	if request.args.get('next'):
		next_url = request.args.get('next')
	return redirect(next_url)


@bp.route('/catecory')
@bp.route('/catecory/<int:page>')
def catecory(page=1):
	pagination = Catecory.objects.paginate(page=page, per_page=20)
	return render_template(
		'getter/catecory.html', 
		pagination=pagination, 
		endpoint='getter.catecory')


@bp.route('/catecory/add', methods=['GET', 'POST'])
@bp.route('/catecory/edit/<id>', methods=['GET', 'POST'])
def edit_catecory(id=None):
	if id:
		catecory = Catecory.objects.get_or_404(pk=id)
		form = CatecoryForm(request.form, obj=catecory)
	else:
		catecory = Catecory()
		form = CatecoryForm(request.form)
	if form.validate_on_submit():
		form.populate_obj(catecory)
		catecory.save()
		return redirect(url_for('getter.catecory'))
	return render_template('getter/edit_catecory.html', form=form)



@bp.route('/album')
@bp.route('/album/<int:page>')
def album(page=1):
	pagination = Album.objects.paginate(page=page, per_page=50)
	return render_template(
		'getter/album.html', 
		pagination=pagination, 
		endpoint='getter.album')


@bp.route('/album/add', methods=['GET', 'POST'])
@bp.route('/edit/<path:id>', methods=['GET', 'POST'])
def edit_album(id=None):
	if id:
		album = Album.objects.get_or_404(pk=id)
		form = AlbumForm(request.form, obj=album)
	else:
		album = Album()
		form = AlbumForm(request.form)
	if form.validate_on_submit():
		form.populate_obj(album)
		album.save()
		return redirect(url_for('getter.album'))
	return render_template('getter/edit_album.html', form=form)

@bp.route('/album/<path:id>/status/<regex("wait|done"):status>')
def album_status(id, status):
	album = Album.objects.get_or_404(pk=id)
	if status == 'wait':
		imgs = json.loads(album.imgs)
		if type(imgs) == unicode:
			imgs = json.loads(imgs)
		title = album.title
		paths = []
		for key, value in imgs.iteritems():
			status, path = value
			if status == 'done':
				paths.append('/getter/img' + os.sep + path)
		return render_template('list.html', images=paths, title=title)
	elif status == 'done':
		album.status = status
		album.save
		next_url = url_for('getter.album')
		if request.args.get('next'):
			next_url = request.args.get('next')
		return redirect(next_url)



@bp.route('/album/<path:id>/delete')
def delete_album(id):
	album = Album.objects.get_or_404(pk=id)
	album.delete()
	next_url = url_for('getter.album')
	if request.args.get('next'):
		next_url = request.args.get('next')
	return redirect(next_url)
