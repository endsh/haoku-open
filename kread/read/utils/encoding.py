# coding: utf-8
import re
import time
import chardet
from urllib import unquote
from .count import chinese_count
from .urls import get_host
from ._file import load_json, save_json

__all__ = [
	"get_encoding", 'coding',
]

common_chinese = re.compile(load_json('chineses.json'))


def get_encoding(text):
	""" get text encoding """
	det = chardet.detect(text)
	if det['encoding']:
		if det['encoding'] == 'ISO-8859-2':
			return 'gb2312'
		return det['encoding'].lower()


def coding(html, output='utf-8'):
	encodings = ["utf-8", "gb2312", "gbk", "gb18030", "big5", "ascii"]
	for enc in encodings:
		try:
			return html.decode(enc).encode(output)
		except UnicodeDecodeError, UnicodeEncodeError:
			pass

	for enc in encodings:
		try:
			return html.decode(enc).encode(output, 'replace')
		except UnicodeDecodeError:
			pass

	for enc in encodings:
		res = html.decode(enc, 'ignore')
		if len(common_chinese.findall(res)) > 200:
			return res.encode(output, 'ignore')

	enc = get_encoding(html)
	if not enc:
		return html

	try:
		res = html.decode(enc, 'ignore')
		if len(common_chinese.findall(res)) > 200:
			return res.encode(output, 'ignore')
	except (LookupError, TypeError):
		return html

	return html
