# coding: utf-8
import conf
from flask import Flask, Blueprint, render_template
from utils import rename


__all__ = [
	"web_index", "web_static", "web_route", "web_run",
]

bp = Blueprint('webtest', __name__)
index = False
prefix = ''
nav_items = []


def create_app():
	app = Flask(__name__,
		static_folder=conf.media_root + '/test',
		template_folder=conf.templates_root + '/test',
		static_url_path='/static')
	app.register_blueprint(bp)

	@app.context_processor
	def default_nav():
		return dict(nav_items=nav_items)

	return app


def web_run(*args, **kwargs):
	if not index:
		web_index('default')
	if 'debug' not in kwargs:
		kwargs['debug'] = True
	return create_app().run(*args, **kwargs)


def web_index(prefix='', caption=u'首页'):
	globals()['index'] = True
	globals()['prefix'] = prefix + '/' if prefix else ''
	web_static('/', 'index', caption)


def web_static(href, id, caption, **context):
	if href != '/':
		nav_items.append((href, id, caption))
	else:
		nav_items.insert(0, (href, id, caption))
	@bp.route(href)
	@rename(id)
	def page():
		context['active_page'] = id
		outs = {}
		for k, v in context.iteritems():
			outs[k] = v() if callable(v) else v
		return render_template(
			'%s%s.html' % (prefix, id), 
			**outs
		)


def web_route(*args, **kwargs):
	return bp.route(*args, **kwargs)
