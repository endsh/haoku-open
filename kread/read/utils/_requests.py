# coding: utf-8
import chardet
import requests
from .worker import do
from .encoding import coding
from .char import u

__all__ = [
	"get_encoding", "get", "fetch_urls",
]


def get_encoding(text):
	""" get text encoding """
	det = chardet.detect(text)
	if det['encoding']:
		if det['encoding'] == 'ISO-8859-2':
			return 'gb2312'
		return det['encoding']


def patch_requests():
	""" requests monkey patch """
	prop = requests.models.Response.content

	def itext(self):
		_content = prop.fget(self)
		return coding(_content, 'utf-8')

	requests.models.Response.itext = property(itext)	

	def icontent(self):
		_content = prop.fget(self)
		encodings = requests.utils.get_encodings_from_content(_content)
		meta_encoding = encodings[0] if encodings else 'utf-8'
		curr_encoding = get_encoding(_content)
		if not curr_encoding:
			curr_encoding = self.encoding
		if curr_encoding.lower() in ('gb2312', 'gbk'):
			curr_encoding = 'gb18030'
		if curr_encoding:
			_content = _content.decode(curr_encoding, 'ignore').encode(meta_encoding, 'ignore')
		return _content
	requests.models.Response.icontent = property(icontent)

patch_requests()


def get(url, **options):
	""" common http get """
	url = u(url)
	TOO_LONG = options.get('max_len') or 0
	human_headers = {
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0',
		'Accept-Encoding':'gzip,deflate,sdch'
	}
	if options.get('headers'):
		human_headers.update(options['headers'])
	allow_types = ['text/html','text/xml']
	if options.get('allow_types'):
		allow_types = options.get('allow_types')
	try:
		r = requests.get(url, headers=human_headers, stream=True)
	except Exception, e:
		raise e
	else:
		if options.get('resp'):
			return r
		if r.status_code < 200 or r.status_code >= 300:
			raise ValueError('status code %d' % r.status_code)
		if allow_types and not '*/*' in allow_types:
			content_type = r.headers.get('content-type', '')
			if not filter(lambda x: content_type.find(x) >= 0, allow_types):
				r.close()
				raise ValueError('content-type [%s] is not allowed' % content_type)
		content_length = int(r.headers.get('content-length', TOO_LONG))
		if TOO_LONG and content_length > TOO_LONG:
			r.close()
			raise ValueError('content-length [%d] is too long' % content_length)

		if options.get('stream'):
			return r.content
			
		html = r.itext
		r.close()
		return html


def fetch_urls(urls, handle=get):
	return dict(do(urls, lambda x: handle(x)))
