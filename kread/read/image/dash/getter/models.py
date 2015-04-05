# coding: utf-8
import time
from mongoengine import signals
from dash.core import mongo


class Domain(mongo.Document):

	STATUS_CHOICES = (('valid', u'有效'), ('invalid', u'废弃'))

	id = mongo.StringField(primary_key=True, max_length=200)
	re_cate = mongo.StringField(max_length=200)
	re_album = mongo.StringField(max_length=200)
	re_page = mongo.StringField(max_length=200)
	re_title = mongo.StringField(max_length=200)
	re_type = mongo.StringField(max_length=200)
	re_image = mongo.StringField(max_length=200)
	cates = mongo.IntField(default=0)
	albums = mongo.IntField(default=0)
	status = mongo.StringField(choices=STATUS_CHOICES)
	last = mongo.FloatField(default=0)

	@classmethod
	def pre_save(cls, sender, document, **kwargs):
		document.last = time.time()

signals.pre_save.connect(Domain.pre_save, sender=Domain)


class Catecory(mongo.Document):

	STATUS_CHOICES = (('wait', u'等待'), ('done', u'完成'), ('error', u'错误'))
	
	id = mongo.StringField(primary_key=True, max_length=200)
	domain = mongo.StringField(max_length=200)
	_type = mongo.StringField(max_length=50)
	status = mongo.StringField(choices=STATUS_CHOICES)
	last = mongo.FloatField(default=0)

	@classmethod
	def pre_save(cls, sender, document, **kwargs):
		document.last = time.time()

signals.pre_save.connect(Catecory.pre_save, sender=Catecory)


class Album(mongo.Document):

	STATUS_CHOICES = (('wait', u'等待'), ('done', u'完成'), ('error', u'错误'))

	id = mongo.StringField(primary_key=True, max_length=200)
	domain = mongo.StringField(max_length=200)
	cate = mongo.StringField(max_length=200)
	imgs = mongo.DictField(default={})
	title = mongo.StringField(max_length=200)
	status = mongo.StringField(choices=STATUS_CHOICES)
	last = mongo.FloatField(default=0)

	@classmethod
	def pre_save(cls, sender, document, **kwargs):
		document.last = time.time()

signals.pre_save.connect(Album.pre_save, sender=Album)