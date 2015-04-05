# coding: utf-8
from flask.ext.mongoengine.wtf import model_form
from .models import Domain, Catecory, Album


DomainForm		= model_form(Domain, only=['id', 're_cate', 're_album', 're_image', 're_page', 're_type', 're_title','status'])
CatecoryForm	= model_form(Catecory, only=['id', 'domain', '_type', 'status'])
AlbumForm		= model_form(Album, only=['id', 'domain', 'cate', 'status'])
