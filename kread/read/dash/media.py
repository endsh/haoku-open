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
		self.hash = {}

		self.add(**options)

		if app is not None:
			self.init_app(app)

	def add(self, **options):
		self.add_css(options.get('css', None))
		self.add_xcss(options.get('xcss', None))
		self.add_js(options.get('js', None))
		self.add_xjs(options.get('xjs', None))
		self.add_footer_js(options.get('jsfooter', None))
		self.add_footer_xjs(options.get('xjsfooter', None))

	def add_css(self, css):
		self._add(self.css, css)

	def add_xcss(self, css):
		self._add(self.xcss, css)
	
	def add_js(self, js):
		self._add(self.js, js)
	
	def add_xjs(self, js):
		self._add(self.xjs, js)

	def add_footer_js(self, js):
		self._add(self.jsfooter, js)

	def add_footer_xjs(self, js):
		self._add(self.xjsfooter, js)

	def _add(self, instance, obj):
		if isinstance(obj, list):
			instance.extend(obj)
		elif isinstance(obj, str):
			instance.append(obj)

	def init_app(self, app):
		self.app = app
		app.context_processor(self.context_processor)
		app.logger.info('media init app.')

	def context_processor(self):
		return dict(
			static_url=self.static_url,
			static_header=self.static_header,
			static_footer=self.static_footer,
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
		link = '<link rel="stylesheet" href="%s">'
		script = '<script src="%s"></script>'
		if self.app.debug:
			htmls = [link % (prefix + x) for x in self.xcss]
			htmls.extend([script % (prefix + x) for x in self.xjs])
		else:
			htmls = [link % self.static_url(x) for x in self.css]
			htmls.extend([script % self.static_url(x) for x in self.js])
		return auto_markup('\n'.join(htmls) + '\n')

	def static_footer(self):
		prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
		script = '<script src="%s"></script>'
		if self.app.debug:
			htmls = [script % (prefix + x) for x in self.xjsfooter]
		else:
			htmls = [script % self.static_url(x) for x in self.jsfooter]
		return auto_markup('\n'.join(htmls) + '\n')

	def static_ie8(self):
		prefix = self.app.config.get('SITE_STATIC_PREFIX', '/static/')
		script = '<script src="%s"></script>'
		if self.app.debug:
			htmls = [script % (prefix + x) for x in self.ie8xjs]
		else:
			htmls = [script % self.static_url(x) for x in self.ie8js]
		return auto_markup('<!--[if lt IE 9]>\n%s\n<![endif]-->\n' % '\n'.join(htmls))