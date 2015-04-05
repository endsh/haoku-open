# coding: utf-8
from flask.ext.restful import Api as _Api


def strip(val, *args):
	if not val:
		return val

	if isinstance(val, dict):
		return dict((x, strip(y) if x not in args else y) for x, y in val.iteritems())
	if isinstance(val, list):
		return list(strip(x) for x in val)

	return val.strip()


class Api(_Api):

	def init_app(self, app):
		super(Api, self).init_app(app)
		if app.config.get('ALL_ERROR_JSON') == True:
			self._all_error_json = True
		else:
			self._all_error_json = False

	def owns_endpoint(self, endpoint):
		if not hasattr(self, '_all_error_json') or self._all_error_json == False:
			return super(Api, self).owns_endpoint(endpoint)
		else:
			return True