# coding: utf-8
import re
from collections import OrderedDict
from utils import clean_html, doc2html, tags

BLOCKS = 'address|article|aside|audio|blockquote|canvas|dd|div|dl|' \
		'fieldset|figcaption|figure|footer|form|h1|h2|h3|h4|h5|h6|header|' \
		'hgroup|hr|li|noscript|ol|output|p|pre|section|table|tfoot|ul|video'.split('|')
TIMESTR = u'20\d{2}[-\./年][01]?\d[-\./月][0-3]?\d日?( [0-2]?\d:|$)'

HEADER_STOPS = re.compile(ur'(导读|编者按|摘要|译文|报道|引读|编者的话|网)([:：】]|$)')
HEADER_BADS = re.compile(TIMESTR + ur'|' + ur'(作者|标题|来源|时间)[ :：]| 媒体人[）)]|禁止.*转载')
FOOTER_STOPS = re.compile(ur'addsfsd')
FOOTER_BADS = re.compile(
	ur'上一篇|下一篇|(责编|责任编辑|文|记者|Via|活动|产品|时间)([:： \/\\]|&nbsp;)|'
	ur'官方微博|微路演|题图来自|更多精彩|【招聘公告】|'
	ur'(AD|热点关注|原标题|来源|编辑|标签|转自|微信|群号|微信号|专题|QQ|群|链接|地址).*[：:]|'
	ur'追究.*法律责任|(本文|原文|文章|相关)(地址|标题|转自|链接|转载|转自)|查看原文|'
	ur'(延伸|关联|更多|相关|推荐|感兴趣的|热门|原创).*(阅读|内容|信息|文章)|'
	ur'(关注|订阅|搜索|回复).*(微信|粉丝)|(微信|粉丝).*(关注|订阅|搜索|回复)|'
	ur'(关注|下载).*(扫描|扫码|二维码)|(扫描|扫码|二维码).*(关注|下载)|'
	ur'(转载|登载|观点|声明).*(允许|禁止|版权|本文|注明)|(允许|禁止|版权|本文|声明).*(转载|登载|观点)|'
	ur'^（.*）$'
)


class Marker(object):

	def __init__(self, input, **options):
		self.input = input
		self.options = options
		self.debug = options.get('debug', True)
		self.title = options.get('title', '+^_^+')
		self.pages = options.get('pages', [])
		self.texts = options.get('texts', [])
		self.doc = clean_html(input, return_doc=True)

	@property
	def content(self):
		if not hasattr(self, '_content'):
			self._content = self.summary()
		return self._content

	def summary(self):
		if self.doc is None:
			return ''

		self.clean_tags()
		self.clean_lines()
		self.clean_header()
		self.clean_footer()
		self.clean()

		return doc2html(self.doc)

	def clean_lines(self):
		self.lines = []
		self.make_node(self.doc)
		self.len = sum([x['len'] for x in self.lines]) + 1

		off = 0
		for line in self.lines:
			line['start'] = float(off) / self.len
			line['start_off'] = off
			off += line['len']
			line['end_off'] = off
			line['end'] = float(off) / self.len

		self.lines = dict((x['node'], x) for x in self.lines)

	def endline(self, node, end=True, tail=False):
		if end == True:
			self.lines.append(dict(node=node, text='', len=0, tail=tail))
		return False, self.lines[-1]

	def make_node(self, node, end=True, link=1):
		if node.tag and node.tag == 'a':
			link = 0.01

		if node.text and node.text.strip():
			end, line = self.endline(node, end)
			line['text'] += node.text.strip()
			line['len'] += len(node.text.strip()) * link
		elif node.tag == 'img':
			end, line = self.endline(node, end)
			line['len'] += 20

		for child in node.getchildren():
			if child.tag and child.tag.lower() in BLOCKS:
				end, link = True, 1
			self.make_node(child, end, link)

		if node.tag and node.tag.lower() in BLOCKS:
			end, link = True, 1
		if node.tail and node.tail.strip():
			end, line = self.endline(node, end, tail=True)
			line['text'] += node.tail.strip()
			line['len'] += len(node.tail.strip())

	def clean_header(self):
		last = self.last_header()
		if last is not None:
			self.drop_header(self.doc, last)

	def last_header(self):
		last = None
		for node in self.doc.iter():
			if node.tag == 'p' and node.xpath('.//img'):
				break
			if node in self.lines:
				if self.lines[node]['end_off'] > 100 \
					and self.lines[node]['end'] > 0.15:
					break
			if HEADER_BADS.search(node.text or '') or node.text == self.title:
				last = node
			elif HEADER_BADS.search(node.tail or '') or node.tail == self.title:
				last = node
			if HEADER_STOPS.search(node.text or '') or HEADER_STOPS.search(node.tail or ''):
				last = node
				break
		return last

	def drop_header(self, node, last):
		self.drop_text(node)
		for child in node.getchildren():
			if child == last:
				if last.tail and re.search(u'^[\)）\]】]', last.tail):
					last.tail = last.tail[1:]
					last.text = u'【摘要】'
				if HEADER_BADS.search(last.tail or '') or last.tail == self.title:
					last.tail = ''
					self.drop(last)
				elif HEADER_BADS.search(last.text or '') or last.text == self.title:
					self.drop(last)
				return True
			elif self.drop_header(child, last):
				return True
		self.drop_tail(node)
		self.drop(node)

	def clean_footer(self):
		last = self.last_footer()
		if last is not None:
			self.drop_footer(self.doc, last)

	def last_footer(self):
		res, last = None, False
		for node in reversed(list(self.doc.iter())):
			if node in self.lines and last == True:
				res = node
				last = False

			if node in self.lines:
				if self.len - self.lines[node]['start_off'] > 100 \
						and self.lines[node]['start'] < 0.7:
					break
			if FOOTER_BADS.search(node.text or '') or node.text == self.title:
				last = True
			elif FOOTER_BADS.search(node.tail or '') or node.tail == self.title:
				last = True
			if FOOTER_STOPS.search(node.text or '') or FOOTER_STOPS.search(node.tail or ''):
				last = True

			if node in self.lines and last == True:
				res = node
				last = False
		return res

	def drop_footer(self, node, last, drop=False):
		if node == last:
			if self.len - self.lines[node]['start_off'] > 100 and self.lines[node]['start'] < 0.7:
				return True
			if FOOTER_BADS.search(last.text or '') or last.text == self.title:
				self.drop_tail(last)
				self.drop(last)
			elif FOOTER_BADS.search(last.tail or '') or last.tail == self.title:
				self.drop_tail(last)
			else:
				self.drop(last)
			return True

		if drop == False:
			for child in node.getchildren():
				if child in self.lines:
					self.line = child
				drop = self.drop_footer(child, last, drop)
			if drop == True:
				self.drop_tail(node)
			return drop
		else:
			self.drop_tail(node)
			self.drop(node)
			return True

	def clean(self):
		self.clean_link()

	def clean_link(self):
		bads = re.compile(u'点击|查看|&gt;&gt;|&lt;&lt;|>>|<<|详细')
		for node in self.doc.iter('a'):
			text = node.text_content() or ''
			if bads.search(text):
				self.drop(node)
			# if 'tag' in node.get('href'):
			# 	self.drop(node)

	def clean_tags(self):
		for node in tags(self.doc, 'form', 'iframe', 'textarea', 'input'):
			if node != self.doc:
				self.drop(node)

	def drop(self, node):
		if self.debug:
			node.attrib['drop'] = 'true'
		else:
			node.drop_tree()

	def drop_text(self, node):
		if node.text and node.text.strip():
			if self.debug:
				node.text = '{{ ' + node.text + ' }}'
			else:
				node.text = ''

	def drop_tail(self, node):
		if node.tail and node.tail.strip():
			if self.debug:
				node.tail = '{{ ' + node.tail + ' }}'
			else:
				node.tail = ''


def img2center(html):
	pass


def clean_content(html, **options):
	return Marker(html, **options).content