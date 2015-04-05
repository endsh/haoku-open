# coding: utf-8
from accounts.sdk.client import Client
from .settings import ACCOUNTS_API_V1_HOST


class BaseAccounts(Client):

	def __init__(self, user):
		super(BaseAccounts, self).__init__(user, ACCOUNTS_API_V1_HOST)

	def login(self, account, password):
		data = dict(account=account, password=password)
		return self.post('/users/login', data=data, https=True)

	def register(self, **kwargs):
		return self.post('/users/register', data=kwargs, https=True)

	def check(self, **kwargs):
		return self.get('/users/check', args=kwargs)

	def find_pass(self, email):
		return self.get('/users/reset_pass', args=dict(email=email))

	def reset_pass(self, **kwargs):
		return self.post('/users/reset_pass', data=kwargs, https=True)

	def access(self, **kwargs):
		return self.get('/access', args=kwargs)

	def profiles(self, ids):
		return self.get('/profiles', args=dict(ids=ids))

	def bind_email(self, code):
		return self.get('/profile/bind_email', args=dict(code=code))
		

class Accounts(BaseAccounts):

	def ssotoken(self):
		return self.get('/ssotoken')

	def logout(self):
		return self.get('/ssologout')

	def info(self):
		return self.get('/users/info')

	def avatar(self, **kwargs):
		return self.post('/profile/avatar', data=kwargs)

	def profile(self, info=False):
		if info == True:
			return self.get('/profile', args=dict(info='true'))
		return self.get('/profile')

	def save_profile(self, **kwargs):
		return self.post('/profile', data=kwargs)

	def change_password(self, **kwargs):
		return self.post('/profile/change-password', data=kwargs)

	def send_access_email(self):
		return self.post('/profile/bind_email')