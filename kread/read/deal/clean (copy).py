# coding: utf-8
import re
from difflib import SequenceMatcher
from lxml.html import fromstring
from utils import word_count, clean_html, doc2html, compose_html
from utils import tags, reverse_tags, get_path, get_domain

__all__ = [
	'Document', 'clean_content', 'img2center',
]

HEAD_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
BAD_TAGS = ['table','article','section']
BAD_XPATH = '|'.join(['.//%s' % x for x in BAD_TAGS])
BLOCK_TAGS = ['div','p','table','td','article','section','pre']
BLOCK_XPATH = '|'.join(['.//%s' % x for x in BLOCK_TAGS])
positiveRe = re.compile('article|body|content|entry|hentry|main|page|pagination|post|text|blog|story', re.I)
negativeRe = re.compile('combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget', re.I)
emailRe = re.compile('\w[\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+|\d{3,}-d+-d+')


class Document(object):
	TEXT_LENGTH_THREASHOLD = 25

	def __init__(self, input, **options):
		self.input = input
		self.url = options.get('url', '')
		self.debug = options.get('debug', False)
		self.title = options.get('title', '^^')
		self.pages = options.get('pages', None)
		self.texts = options.get('texts', None)
		self.domain = get_domain(self.url)
		self.options = options
		self.doc = clean_html(input, return_doc=True)
		self.text = self.doc.text_content()
		self.len = word_count(self.text) if self.text else 0

	def summary(self):
		if hasattr(self, 'output'):
			return self.output

		if self.doc is None:
			return ''

		MIN_LEN = self.options.get(
			'min_text_length',
			self.TEXT_LENGTH_THREASHOLD,
		)

		for node in tags(self.doc, 'form', 'iframe', 'textarea', 'table', 'input'):
			if node != self.doc:
				node.drop_tree()

		for img in self.doc.xpath('.//img'):
			if img.get('data-original'):
				img.set('src', img.get('data-original'))
			if img.get('original'):
				img.set('src', img.get('original'))
			if re.search('\/static\/|\.gif', img.get('src', '')):
				self.drop(img)

		click = re.compile(u'点击|>>')
		for node in self.doc.iter('a'):
			if not node.getchildren():
				if click.search(node.text_content()):
					self.drop(node)
			else:
				for child in node.getchildren():
					if click.search(child.text or ''):
						self.drop(child)

		imgs = []
		for child in self.doc.getchildren():
			res = self.is_need_drop(child, False if imgs else True)
			if res == 'img':
				imgs.append(child)
				continue
			elif res == False:
				break

			self.drop(child)
			for img in imgs:
				self.drop(img)
			imgs = []

		# imgs = []
		# for child in reversed(self.doc.getchildren()):
		# 	res = self.is_need_drop(child, False if imgs else True)
		# 	if res == 'img':
		# 		imgs.append(child)
		# 		continue
		# 	elif res == False:
		# 		break

		# 	self.drop(child)
		# 	for img in imgs:
		# 		self.drop(img)
		# 	imgs = []

		# for child in self.doc.getchildren():
		# 	if self.is_bad_node(child):
		# 		self.drop(child)
		# 	elif self.texts is not None:
		# 		text = child.text_content().strip()
		# 		if text and text in self.texts:
		# 			self.drop(child)
		# 		else:
		# 			self.texts.add(text)

		self.output = self.clean()
		return self.output

	def is_bad_node(self, node):
		text = node.text_content().strip()

		if node.tag.lower() in 'img|br':
			return False
		
		if not text and not node.getchildren():
			return True

		for img in node.xpath('.//img'):
			if self.title in img.get('alt', '') \
					or self.title in img.get('title', ''):
				return False

		text_len = word_count(text)
		link_len, link_cnt = 0, 0
		for link in node.findall('.//a'):
			link_cnt += 1
			if not link.text_content():
				continue
			link_len += word_count(link.text_content())

		if link_cnt > 1 and text_len > 1 and link_len / float(text_len) > 0.4:
			return True

		if link_cnt > 1 and text_len / float(link_cnt) < 10:
			return True

		if link_cnt > 1 and node.cssselect('li a'):
			return True

		block_cnt = len(node.xpath(BAD_XPATH))
		if link_cnt > 0 and block_cnt > 1 and len(node.cssselect('pre')) == 0:
			return True

		if text_len / float(self.len + 1) < 0.15 or text_len < 100:
			if re.search('\d{3,}-\d+-\d+', text):
				return True
			# filterRe = re.compile(u'点击(.*)(进入|观看)|^事实\+$')
			# if filterRe.match(text):
			# 	return True

		return False

	def is_need_drop(self, node, short=True):
		if node.tag.lower() == 'img':
			return False

		if self.is_bad_node(node):
			return True

		text = node.text_content().strip()
		text_len = word_count(text)

		if text_len == 0 and not node.xpath('.//img'):
			return True

		if short and text_len < 8 and not node.xpath('.//img'):
			return True

		if short and text_len < 20 and not node.xpath('.//img') \
				and re.search(u'^【.*】|^（.*）|^\(.*\)|【.*】$|（.*）$|\(.*\)$', text):
			return True

		filterRe = re.compile(
			u"(上一篇|下一篇|AD|热点关注|原标题|来源|编辑|标签|转自|微信|群号|微信号)[：:]|"
			u"追究.*法律责任|关联阅读|请点击|#换成@|关注|(本文|原文|文章)(地址|标题|转自|链接|转载)|原创文章|"
			u"查看原文|延伸阅读|(推荐|相关)文章|转载请注明|继续浏览|正文.*结束|版 权 所 有|"
			u"(转载|登载|观点|允许).*(禁止|版权|本文)|(允许|禁止|版权|本文).*(转载|登载|观点)|"
			u"(关注|订阅|搜索|回复).*微信|微信.*(关注|订阅|搜索|回复)|【.*记者|版权声明|"
			u"(关注|下载).*(扫描|扫码|二维码)|(扫描|扫码|二维码).*(关注|下载)|专题：|"
			u"更多.*(内容|信息|文章).*请|责编|QQ群|^【.*】$|^（.*）$")

		if text_len / float(self.len + 1) < 0.15 or text_len < 100:
			if short and self.title and self.title in text:
				return True
			if emailRe.search(text) or filterRe.search(text):
				return True

		for link in node.xpath('.//a'):
			href = link.get('href', '')
			if href == self.url or self.pages and href in self.pages:
				return False if link.xpath('.//img') else True
			path = get_path(href)
			domain = get_domain(href)
			if domain == self.domain and path in ['/', ''] and link.xpath('.//img'):
				self.drop(link)

		# for img in node.xpath('.//img'):
		# 	alt = img.get('alt')
		# 	if alt and len(alt) < 50:
		# 		if re.search(u'微信二维码', alt):
		# 			return True
		# 		if len(SequenceMatcher(self.title, alt)\
		# 				.get_matching_blocks()) / float(len(self.title)) < 0.3:
		# 			return False
			
		# 	title = img.get('title')
		# 	if title and len(title) < 50:
		# 		if re.search(u'微信二维码', title):
		# 			return True
		# 		if len(SequenceMatcher(self.title, title)\
		# 				.get_matching_blocks()) / float(len(self.title)) < 0.3:
		# 			return False

		if node.xpath('.//img'):
			return 'img'

		return False

	def drop(self, node):
		if self.debug:
			node.attrib['class'] = 'k-drop-tree'
		else:
			node.drop_tree()

	def drop_tag(self, parent, node):
		if parent is not None:
			previous = node.getprevious()
			next = node.getnext()
			if node.text:
				if previous is not None:
					previous.tail = (previous.tail or '') + node.text
				else:
					parent.text = (parent.text or '') + node.text

			for child in node.getchildren():
				node.addprevious(fromstring(doc2html(child)))

			previous = node.getprevious()
			if node.tail:
				if previous is not None:
					previous.tail = (previous.tail or '') + node.tail
				else:
					parent.text = (parent.text or '') + node.tail
			node.drop_tree()

	def clean(self):
		for node in list(self.doc.iter()):
			parent = node.getparent()
			previous = node.getprevious()
			next = node.getnext()

			if node.tag == 'a' and not node.get('href', '').startswith('http') \
					or node.tag == 'img' and not node.get('src', '').startswith('http'):
				node.drop_tree()
				continue

			if parent is not None and node.tag in ['a', 'span', 'font']:
				if not (node.text and node.tag == 'a' \
						and (node.get('href', '^^').strip() == node.text.strip() or u'下载' in node.text)):
					if node.tag != 'a' \
							or node.getchildren() \
							or node.text and not re.search(ur'[\[\>\]]', node.text.strip()):
						self.drop_tag(parent, node)
						continue
					node.drop_tree()
					continue

		return compose_html(doc2html(self.doc))


def replace_node(format, node):
	if node.getparent() is not None:
		tail = node.tail
		node.tail = ''
		newnode = fromstring(format % doc2html(node))
		newnode.tail = tail
		node.getparent().replace(node, newnode)
	return node


def img2center(doc, title):
	for node in list(doc.iter()):
		parent = node.getparent()
		previous = node.getprevious()
		next = node.getnext()
	
		for key, value in node.attrib.items():
			if key not in ['src', 'href']:
				node.attrib.pop(key)
			if key in ['style'] and 'center' in value:
				node.set('style', 'text-align:center')

		if node.tag == 'a':
			node.set('target', '_blank')
		elif str(node.tag).lower() in 'h1|h2':
			node.tag = 'h3'
		elif node.tag == 'img' and parent is not None:
			replace_node('<div class="k-img" style="text-align:center;">%s</div>', node)

			if previous is None and parent.text and parent.text.strip() \
					or previous is not None \
					and (previous.tail or str(previous.tag).lower() not in 'p|div'):
				node.addprevious(fromstring('<br>'))
			if node.tail and node.tail.strip():
				node.addnext(fromstring('<br>'))
			elif next is not None and str(next.tag).lower() not in 'p|div':
				next.addprevious(fromstring('<br>'))

			if next is not None and next.text and next.text.strip():
				text = next.text.strip()
				if word_count(text) < 40 \
						and (not re.match(u'.*[:.?!：。？！…]$', text) \
							or re.search(u'制图|资料图|图片|图|摄', text)) \
						and not re.search(u'(\d+|[一二三四五六七八九十]+)[、.]', text):
					replace_node('<div style="text-align:center;">%s</div>', next)
					continue

			if previous is None and not parent.text:
				pprevious = parent.getprevious()
				if pprevious is not None \
						and not pprevious.xpath(BLOCK_XPATH):
					text = pprevious.text_content().strip()
					if word_count(text) < 40 \
							and (not re.match(u'.*[:.?!：。？！…]$', text) \
								or re.search(u'制图|资料图|图片|图|摄', text)) \
							and not re.search(u'(\d+|[一二三四五六七八九十]+)[、.]', text):
						pprevious.set('style', 'text-align:center')
						continue

			if not node.tail and node.getnext() is None:
				pnext = parent.getnext()
				if pnext is not None \
						and not pnext.xpath(BLOCK_XPATH):
					text = pnext.text_content().strip()
					if word_count(text) < 40 \
							and (not re.match(u'.*[:.?!：。？！…]$', text) \
								or re.search(u'制图|资料图|图片|图|摄', text)) \
							and not re.search(u'(\d+|[一二三四五六七八九十]+)[、.]', text):
						pnext.set('style', 'text-align:center')
						continue

	for node in doc.iter('pre'):
		if not node.getchildren():
			node.text = re.sub('(^|\r|\n) *\d+', '', (node.text or ''))

	for node in doc.iter('img'):
		node.set('alt', title)
		node.set('ttile', title)


def clean_content(html, **options):
	return Document(html, **options).summary()
