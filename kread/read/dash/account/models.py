# coding: utf-8
from sqlalchemy_utils import PasswordType
from ..core import db, SessionMixin

class Role(db.Model, SessionMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40), unique=True)
	desc = db.Column(db.String(50))

	def __unicode__(self):
		return self.name


class Account(db.Model, SessionMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(40), unique=True)
	password = db.Column(
		PasswordType(
			schemes=[
				'pbkdf2_sha512',
				'md5_crypt',
			],
			deprecated=['md5_crypt'],
		)
	)
	email = db.Column(db.String(40), unique=True)
	email_verify = db.Column(db.String(40))
	reset_verify = db.Column(db.String(40))
	phone = db.Column(db.String(20), unique=True)
	phone_verify = db.Column(db.String(40))
	safe_question = db.Column(db.String(40))
	safe_anwser = db.Column(db.String(40))
	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
	role = db.relationship('Role')

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	def __unicode__(self):
		return self.username
