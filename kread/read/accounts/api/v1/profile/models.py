# coding: utf-8
from simin.web.core import SessionMixin, sql


class Profile(sql.Model, SessionMixin):
	Column, String = sql.Column, sql.String
	
	id = sql.Column(sql.Integer(), primary_key=True)
	nickname = Column(String(40))
	birthday = Column(sql.Integer())
	sex = Column(String(20))
	city = Column(String(40))
	site = Column(String(100))
	signature = Column(String(100))
	intro = Column(String(100))
	avatar = Column(String(100))