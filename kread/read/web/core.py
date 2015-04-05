# coding: utf-8
import conf
import random
from simin.web.media import MediaManager
from simin.web.verify import VerifyManager
from accounts.sdk.sso import SSOManager
from accounts.client.v1 import BaseAccounts, Accounts
from api.client.v1 import BaseReader, Reader

sso = SSOManager()
sso.setup_user(
	publics=dict(
		accounts=BaseAccounts,
		read=BaseReader,
	),
	privates=dict(
		accounts=Accounts,
		read=Reader,
	),
)

media = MediaManager(
	css=['css/read.min.css'],
	xcss=['libs/bootstrap/css/bootstrap.css', 'dist/css/read.css'],
	js=['js/read.min.js'],
	xjs=[
		'libs/jquery-1.11.1.js',
		'libs/jquery.form.js',
		'libs/bootstrap/js/bootstrap.js', 
		'dist/js/read.js',
	],
)

verify = VerifyManager()


icon_ad = [u"""<script type="text/javascript">
    /*200*200 创建于 2014-12-18*/
    var cpro_id = "u1866249";
</script>
<script src="http://cpro.baidustatic.com/cpro/ui/c.js" type="text/javascript"></script>
""",

u"""<script type="text/javascript">
    /*200*200 创建于 2014-12-18*/
    var cpro_id = "u1866262";
</script>
<script src="http://cpro.baidustatic.com/cpro/ui/c.js" type="text/javascript"></script>
""",

u"""<script type="text/javascript">
    /*200*200 创建于 2014-12-18*/
    var cpro_id = "u1866264";
</script>
<script src="http://cpro.baidustatic.com/cpro/ui/c.js" type="text/javascript"></script>
"""
]

def good_hots(hots):
	if not hots:
		return hots
	q = random.randint(0, 4)
	count = 0
	for tag, icon in hots.iteritems():
		if count < q and random.randint(0, 1) == 1 and count < 3:
			hots[tag] = icon_ad[count]
			count += 1		
	return hots


def init_core(app):
	sso.init_app(app)
	media.init_app(app)
	verify.init_app(app)