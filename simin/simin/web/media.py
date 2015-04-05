# coding: utf-8
import os
import hashlib
from .filters import auto_markup

__all__ = [
	'MediaManager',
]


class MediaManager(object):

	def __init__(self, app=None, **options):
		self.css = []
		self.xcss = []
		self.js = []
		self.xjs = []
		self.jsfooter = []
		self.xjsfooter = []
		self.ie8js = ['ie8.min.js']
		self.ie8xjs = [
			'libs/html5shiv.js', 
			'libs/respond.src.js', 
			'libs/respond.matchmedia.addListener.src.js',
		]
		self.admin_css = []
		self.admin_xcss = []
		self.admin_js = []
		self.admin_xjs = []
		self.admin_jsfooter = []
		self.admin_xjsfooter = []
		self.hash = {}

		self.add(**options)

		if app is not None:
			self.init_app(app)

	def add(self, **options):
		for key in ['css', 'xcss', 'js', 'xjs', 'jsfooter', 'xjsfooter']:
			self._add(key, options.get(key, None))
			self._add('admin_%s' % key, options.get('admin_%s' % key, None))

	def _add(self, instance, obj):
		if isinstance(instance, str):
			instance = getattr(self, instance)

		if isinstance(obj, list):
			instance.extend(obj)
		elif isinstance(obj, str):
			instance.append(obj)

	def init_app(self, app):
		self.app = app
		app.context_processor(self.context_processor)

	def context_processor(self):
		return dict(
			static_url=self.static_url,
			static_header=self.static_header,
			static_footer=self.static_footer,
			static_admin_header=self.static_admin_header,
			static_admin_footer=self.static_admin_footer,
			static_ie8=self.static_ie8,
		)

	def static_url(self, filename):
		if filename not in self.hash:
			path = os.path.join(self.app.static_folder, filename)
			if not os.path.isfile(path):
				return filename

			with open(path, 'r') as fd:
				content = fd.read()
				hsh = hashlib.md5(content).hexdigest()

			self.app.logger.info('Generate %s md5sum: %s' % (filename, hsh))
			prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
			self.hash[filename] = '%s%s?v=%s' % (prefix, filename, hsh[:5])
		return self.hash[filename]

	def static_header(self):
		prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
		link = '    <link rel="stylesheet" href="%s">'
		script = '    <script src="%s"></script>'
		if self.app.debug:
			htmls = [link % self.static_url(x) for x in self.xcss]
			htmls.extend([script % self.static_url(x) for x in self.xjs])
		else:
			htmls = [link % self.static_url(x) for x in self.css]
			htmls.extend([script % self.static_url(x) for x in self.js])
		return auto_markup('\n'.join(htmls) + '\n')

	def static_footer(self):
		prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
		script = '    <script src="%s"></script>'
		if self.app.debug:
			htmls = [script % self.static_url(x) for x in self.xjsfooter]
		else:
			htmls = [script % self.static_url(x) for x in self.jsfooter]
		return auto_markup('\n'.join(htmls) + '\n')

	def static_admin_header(self):
		prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
		link = '    <link rel="stylesheet" href="%s">'
		script = '    <script src="%s"></script>'
		if self.app.debug:
			htmls = [link % self.static_url(x) for x in self.admin_xcss]
			htmls.extend([script % self.static_url(x) for x in self.admin_xjs])
		else:
			htmls = [link % self.static_url(x) for x in self.admin_css]
			htmls.extend([script % self.static_url(x) for x in self.admin_js])
		return auto_markup('\n'.join(htmls) + '\n')

	def static_admin_footer(self):
		prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
		script = '    <script src="%s"></script>'
		if self.app.debug:
			htmls = [script % self.static_url(x) for x in self.admin_xjsfooter]
		else:
			htmls = [script % self.static_url(x) for x in self.admin_jsfooter]
		return auto_markup('\n'.join(htmls) + '\n')

	def static_ie8(self):
		prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
		script = '    <script src="%s"></script>'
		if self.app.debug:
			htmls = [script % self.static_url(x) for x in self.ie8xjs]
		else:
			htmls = [script % self.static_url(x) for x in self.ie8js]
		return auto_markup('    <!--[if lt IE 9]>\n%s\n    <![endif]-->\n' % '\n'.join(htmls))