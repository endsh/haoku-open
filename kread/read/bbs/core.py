# coding: utf-8
from simin.web.media import MediaManager
from simin.web.verify import VerifyManager
from accounts.sdk.sso import SSOManager
from accounts.client.v1 import BaseAccounts, Accounts

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
	css=['css/bbs.min.css'],
	xcss=['libs/bootstrap/css/bootstrap.css', 'dist/css/bbs.css'],
	js=['js/bbs.min.js'],
	xjs=['libs/jquery-1.11.1.js', 'libs/jquery.form.js', 'libs/bootstrap/js/bootstrap.js', 'dist/js/bbs.js'],
)

verify = VerifyManager()


def init_core(app):
	sso.init_app(app)
	media.init_app(app)
	verify.init_app(app)