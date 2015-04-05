# coding: utf-8
import re
from collections import defaultdict
from lxml.html import HTMLParser, soupparser, fromstring, tostring
from lxml.etree import XMLSyntaxError
from .urls import get_domain, resolve_url

__all__ = [
	"html2text", "doc2text", "html2doc", "doc2html", "child2html",
	"clean_empty_node", "clean_doc", "clean_html", 'compose_html',
	"tags", "reverse_tags", 'html2urls', 'html2others', 'doc2urls',
	"tag2text",
]

UTF8_PARSER = HTMLParser(encoding='utf-8')
BLOCK_TAGS = 'p|div|pre|code|blockquote|table|article|section|h1|h2|h3|h4|h5|h6|ul|ol'.split('|')


def html2text(html, code=True):
	return doc2text(html2doc(html), code=code)


def doc2text(doc, code=True):
	if code:
		[x.drop_tree() for x in doc.iter('pre')]
	return doc.text_content()


def html2doc(html, url=None, retry=0):
	try:
		doc = fromstring(html, parser=UTF8_PARSER)
	except XMLSyntaxError:
		doc = soupparser.fromstring(html)

	if doc.find('body') is None and 'html' in html and retry < 1:
		html = re.sub('\0', '', html)
		return html2doc(html, url, retry + 1)
	if url is not None:
		doc.make_links_absolute(url, resolve_base_href=True)
	return doc


def doc2html(doc, default=''):
	if doc is not None:
		return tostring(doc, encoding='utf-8').decode('utf-8')
	else:
		return default


def child2html(doc, default=''):
	if doc is None:
		return default

	html = ''
	for node in doc.getchildren():
		html += doc2html(node)
	return html


def clean_empty_node(doc):
	count = 0
	for node in doc.iter():
		if node.tag in ['img', 'br', 'meta']:
			continue

		if node.tag == 'link' \
				and node.attrib.get('rel', '') != 'stylesheet' \
				and node.attrib.get('type', '') != 'text/css':
			continue

		if node.getparent() is not None and (not node.text or not node.text.strip()) \
				and not node.getchildren() \
				or 'bdshare' in node.get('id', '') \
				or 'bdshare' in node.get('class', '') \
				or 'neirong-shouquan' in node.get('class', ''):
			node.drop_tree()
			count += 1

	if count >= 1:
		clean_empty_node(doc)

	return doc


def clean_doc(doc, return_html=False):
	xpath = './/script | .//style | .//noscript | .//comment()'
	[x.drop_tree() for x in doc.xpath(xpath)]
	clean_empty_node(doc)
	return doc2html(doc) if return_html else doc


def clean_html(html, url=None, return_doc=False):
	doc = html2doc(html, url)
	clean_doc(doc)
	return doc if return_doc else doc2html(doc)


def compose_br(doc):
	for node in doc.iter('haoku-br'):
		parent = node.getparent()
		previous = node.getprevious()
		next = node.getnext()
		second_next = next.getnext() if next is not None else None

		if parent is not None and node.tag == 'haoku-br':
			need_drop = False
			if previous is None and (not parent.text or not parent.text.strip()):
				need_drop = True
			elif previous is not None \
					and previous.tag in BLOCK_TAGS \
					and (not previous.tail or not previous.tail.strip()):
				need_drop = True
			elif not node.tail or not node.tail.strip():
				if next is None or next.tag in BLOCK_TAGS:
					need_drop = True
				elif next.tag == 'haoku-br' and (not next.tail or not next.tail.strip()):
					if second_next is None or second_next.tag in BLOCK_TAGS:
						need_drop = True
					elif second_next.tag == 'haoku-br':
						need_drop = True
					
			if need_drop:
				node.drop_tree()


def compose_pre(doc):
	for node in tags(doc, 'pre', 'code'):
		if not node.getchildren() and node.text:
			text = node.text
			lines = text.splitlines()
			lens = len(lines)
			while len(filter(lambda x: x and x[0] == ' ', lines)) == lens:
				lines = map(lambda x: x[1:], lines)
			node.text = re.sub(ur'(\n[\r\t ]*){3,}', '\n\n', '\n'.join(lines))
			node.text = re.sub(ur'[\r\n\t ]+$', '', node.text)


def compose_space(doc):
	if str(doc.tag).lower() in ['pre', 'code']:
		return

	if doc.text:
		if doc.tag == 'p' and not doc.text.startswith('   '):
			doc.text = doc.text.rstrip()
		else:
			doc.text = doc.text.strip()
			
		if doc.text == '&nbsp;':
			doc.text = ''

	if doc.tail:
		doc.tail = doc.tail.strip()
		if doc.tail == '&nbsp;':
			doc.tail = ''

	for child in doc.getchildren():
		compose_space(child)


def compose_html(html):
	html = re.sub(ur'<br\/?>', '<haoku-br/>', html)
	doc = html2doc(html)
	compose_br(doc)
	compose_pre(doc)
	compose_space(doc)
	return re.sub(ur'<haoku-br><\/haoku-br>', '<br>', doc2html(doc))


def tags(node, *tag_names):
	xpath = ' | '.join('.//%s' % x for x in tag_names)
	for e in node.xpath(xpath):
		yield e


def reverse_tags(node, *tag_names):
	xpath = ' | '.join('.//%s' % x for x in tag_names)
	for e in reversed(node.xpath(xpath)):
		yield e


def html2urls(html, url=None, name=True):
	return doc2urls(html2doc(html, url), url and get_domain(url), other=False, name=name)


def html2others(html, url, name=True):
	return doc2urls(html2doc(html, url), domain=get_domain(url), other=True, name=name)


def doc2urls(doc, domain=None, other=False, name=True):
	urls = defaultdict(list) if name else set()
	for link in doc.iter('a'):
		url = link.get('href')
		text = link.text_content() or link.get('title')
		if not url or not url.strip() or len(url) > 256 \
				or not url.startswith('http://') \
				or re.search('bbs|[\/.](t|v|d)\.|video|about|thread|forum|down', url) \
				or not text or not text.strip() \
				or not other and domain and domain != get_domain(url) \
				or other and domain and domain == get_domain(url):
			continue
		url = resolve_url(url)
		if name:
			urls[url.strip()].append(text.strip())
		else:
			urls.add(url.strip())
	return urls if name else list(urls)


def tag2text(doc, tag, **kwargs):
	default = kwargs.pop('default', '')
	bad = kwargs.pop('bad', None)
	for node in doc.iter(tag):
		for key, value in kwargs.iteritems():
			if key not in node.attrib and value != None \
					or key in node.attrib and node.attrib[key].lower() != value.lower():
				break
		else:
			if tag == 'link':
				text = node.attrib.get('href', default)
			elif tag == 'meta':
				text = node.attrib.get('content', default)
			else:
				text = node.text_content()
			if bad is not None and bad in text:
				continue
			return text 
	return default