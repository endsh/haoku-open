# coding: utf-8
from flask import Blueprint, request, render_template
from flask import redirect, url_for
from .forms import DomainForm, CatecoryForm, AlbumForm
from .models import Domain, Catecory, Album

bp = Blueprint('getter', __name__)


@bp.route('/')
def domain(page=1):
	pagination = Domain.objects.paginate(page=page, per_page=20)
	return render_template(
		'getter/domain.html', 
		pagination=pagination, 
		endpoint='getter.domain')