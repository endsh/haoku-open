# coding: utf-8
import conf
from db import OssFile, LocalFile
from simin.web.media import MediaManager
from simin.web.verify import VerifyManager
from accounts.sdk.sso import SSOManager
from accounts.client.v1 import BaseAccounts, Accounts
from .settings import AVATAR_FILE_CONF

sso = SSOManager()
sso.setup_user(
	publics=dict(
		accounts=BaseAccounts,
	),
	privates=dict(
		accounts=Accounts,
	),
)

media = MediaManager(
	css=['css/accounts.min.css'],
	xcss=['libs/bootstrap/css/bootstrap.css', 'dist/css/accounts.css'],
	js=['js/accounts.min.js'],
	xjs=['libs/jquery-1.11.1.js', 'libs/jquery.form.js', 'libs/bootstrap/js/bootstrap.js', 'dist/js/accounts.js'],
)

verify = VerifyManager()

if conf.RELEASE:
	AVATAR = OssFile(AVATAR_FILE_CONF)
else:
	AVATAR = LocalFile(AVATAR_FILE_CONF)

def init_core(app):
	sso.init_app(app)
	media.init_app(app)
	verify.init_app(app)