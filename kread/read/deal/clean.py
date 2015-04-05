# coding: utf-8
import re
from collections import OrderedDict
from xml.sax.saxutils import escape, quoteattr
from utils import clean_html, doc2html, tags, url2filetype

BLOCKS = 'address|article|aside|audio|blockquote|canvas|dd|div|dl|' \
		'fieldset|figcaption|figure|footer|form|h1|h2|h3|h4|h5|h6|header|' \
		'hgroup|hr|li|noscript|ol|output|p|pre|section|table|tfoot|td|ul|video'.split('|')
SKIPS = 'dl|h1|h2|h3|h4|h5|h6|ol|ul'.split('|')
HEXS = 'h1|h2|h3|h4|h5|h6'.split('|')
TIMESTR = u'20\d{2}[-\./年][01]?\d[-\./月][0-3]?\d日?( [0-2]?\d:|$)'
LABEL = re.compile(u'摄|图|表|资料')
SEN = re.compile('[.:：、]')
BADS = re.compile(TIMESTR +
	u'|^.{0,8}(标签|分享|共享|喜欢|标题|来源|原文|作者|链接|相关|文章|专题|点击查看|转自|修正|'
	u'上一|下一|上页|下页|Via|编辑|推荐|责编|微信联系|媒体人|题图来自|版权|声明|关联).{0,4}([ /\\:：】）]|$)'
	ur'|^.{0,16}(客服QQ|群|地址|地址|微信|关注).{0,4}([ /\\:：】）]|$)'
	ur'|^.{0,4}(关键词|AD)([ /\\:：】）]|$)'
	ur'|^.{0,2}(文/|记者|□)'
	ur'|^.{0,4}(公司|时间|产品|网|热线|电话)[:：]'
	ur'|^[【\[].{0,30}(记者|作者)'
	ur'|(发送|关注|回复|搜索|订阅|收听).{0,30}(微信|公众号|微博)'
	ur'|(微信|公众号|微博).{0,30}(发送|回复|搜索|订阅|收听)'
	ur'|(文章|资讯|阅读|版权|(想|欲)了解|注明|禁止|不代表).{0,30}(更多|分享|转载|未经|延伸|所有|取自|来自|转自)'
	ur'|(更多|分享|转载|未经|延伸|所有|取自|来自|转自).{0,30}(文章|资讯|阅读|版权|(想|欲)了解|注明|禁止|不代表)'
	ur'|扫描.{0,30}二维码|(扫码|APP|软件|打包)下载|附带极客闹'
	ur'|(发送到|邮箱|投递).{0,30}@|致电.{0,4}[\d\-\\\/]{6,15}'
	ur'|^.{0,6}(事实\+|下页为)|正文已结束'
)


class Marker(object):

	def __init__(self, title, doc):
		self.title = title
		self.doc = doc

	@property
	def content(self):
		if not hasattr(self, '_content'):
			self._content = self.summary()
		return self._content

	def summary(self):
		self.html = ''
		self.curr_tag = 'p'
		self.curr_node = None
		self.ready = False
		self.last = 'text'
		self.mark(self.doc)
		self.replace()
		return self.html

	def append(self, text, node=None):
		if self.ready == False:
			center = node is not None and node.tag == 'img'
			self.html += self.format(self.curr_tag, self.curr_node, center=center)
			self.ready = True
		if node is not None and node != self.curr_node:
			self.html += self.format(node.tag, node)
		self.last = 'img' if node is not None and node.tag == 'img' else 'text' 
		self.html += escape(text)

	def format(self, tag, node=None, attrs=None, center=False):
		attrs = attrs or {}
		if node is not None:
			if node.tag == 'a':
				attrs = {'href':node.get('href', ''), 'target':'_blank'}
			elif node.tag == 'img':
				attrs = {
					'src': node.get('src'),
					'title': self.title,
					'alt': self.title,
				}

			if self.last == 'img' and node == self.curr_node and not node.getchildren():
				if 4 <= len(node.text or '') <= 36 and (LABEL.search(node.text) \
						or 'center' in node.get('align', '').lower() \
						or 'center' in node.get('style', '').lower()):
					attrs['align'] = 'center'
					attrs['class'] = 'article-img-label'

		if center == True:
			attrs['align'] = 'center'
			attrs['class'] = 'article-img'

		if tag in HEXS:
			tag = 'h3'

		attrs = ['%s=%s' % (x, quoteattr(y)) for x, y in attrs.iteritems()]
		attrs = ' ' + ' '.join(attrs) if attrs else ''
		return '<%s%s>' % (tag, attrs)

	def update(self, tag='p', node=None, ready=False):
		if self.ready == True:
			self.html += '</%s>' % self.curr_tag
		self.curr_tag = tag
		self.curr_node = node
		self.ready = ready

	def start(self, node=None, end=False):
		if node is not None:
			if node.tag in BLOCKS and node.tag not in SKIPS or node.tag == 'br':
				self.update(node=node)
			elif node.tag in SKIPS:
				self.update('p' if end else node.tag, None if end else node)
			else:
				return False
		else:
			self.update()
		return True

	def end(self, node=None):
		if not self.start(node, end=True):
			self.html += '</%s>' % node.tag

	def mark(self, node):
		if self.hasdiss(node):
			return

		self.start(node)
		if node.text and node.text.strip():
			self.append(node.text.strip(), node)

		if node.tag == 'img':
			self.end()
			self.append('', node)
			self.end()
		else:
			for child in node.getchildren():
				self.mark(child)
			self.end(node)

		if node.tail and node.tail.strip():
			self.append(node.tail.strip())

	def hasdiss(self, node):
		tags = 'pre|table'.split('|')
		if node.tag in tags:
			self.end()
			self.html += self.diss(node)
			self.end()
			return True
		return False

	def diss(self, node):
		if node.tag == 'pre':
			return self.code(node)
		elif node.tag == 'table':
			return self.table(node)
		else:
			return self.clean(node)

	def code(self, node):
		tags = 'ol|li|ul|span|dl|dt'.split('|')
		for child in node.iter():
			if child.tag not in tags and child != node:
				return self.clean(node)
		
		if not node.getchildren() and node.text:
			text = node.text
		else:
			def pre2text(node):
				text = ''
				if node.text:
					text = node.text + '\n' if node.tag != 'span' else node.text
				for child in node.getchildren():
					text += pre2text(child)
				if node.tail:
					text += node.tail + '\n' if node.tag != 'span' else node.tail
				return text

			text = pre2text(node)

		lines = text.splitlines()
		lens = len(lines)
		while len(filter(lambda x: x and x[0] in '0123456789 ', lines)) == lens:
			lines = map(lambda x: x[1:], lines)
		text = re.sub(ur'(\n[\r\t ]*){3,}', '\n\n', '\n'.join(lines))
		text = re.sub(ur'[\r\n\t ]+$', '', text)
		return '<pre>%s</pre>' % escape(text)

	def table(self, node):
		tds = node.xpath('.//td')
		if len(tds) == 1:
			children = tds[0].getchildren()
			if len(children) == 1 and children[0].tag == 'pre':
				return self.code(children[0])
		return self.clean(node, {'class':'table table-striped'})

	def clean(self, node, attrs=None):
		html = self.format(node.tag, attrs=attrs)
		if node.text:
			html += escape(node.text)
		for child in node.getchildren():
			html += self.clean(child)
		html += '</%s>' % node.tag
		if node.tail:
			html += escape(node.tail)
		return html

	def replace(self):
		text = u'０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
		repalce = u'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
		num = dict((x, y) for x, y in zip(text, repalce))
		self.html = re.sub(u'[%s]' % text, lambda x: str(num[x.group(0)]), self.html)


class Cleaner(object):

	def __init__(self, input, **options):
		self.input = input
		self.options = options
		self.debug = options.get('debug', False)
		self.title = options.get('title', '+^_^+')
		self.pages = options.get('pages', [])
		self.texts = options.get('texts', None)
		self.doc = clean_html(input, return_doc=True)

	@property
	def content(self):
		if not hasattr(self, '_content'):
			self._content = self.summary()
		return self._content

	def summary(self):
		if self.doc is None:
			return ''

		self.clean_bads()
		self.clean_nodes()
		self.clean_tags()

		html = self.clean()
		if self.texts is not None:
			html = self.clean_texts(html)

		return html

	def clean_bads(self):
		for node in tags(self.doc, 'form', 'iframe', 'textarea', 'input'):
			if node != self.doc:
				self.drop(node)

		jpgs = 'jpg|jpeg|png|gif|bmp'.split('|')
		for node in tags(self.doc, 'img', 'a'):
			if node.tag == 'img':
				width = to_int(node.get('width'))
				height = to_int(node.get('height'))
				src = node.get('src', '')
				if not src.startswith('http://') \
						or 'themes' in src \
						or (url2filetype(src) or '').lower() not in jpgs \
						or width is not None and height is not None \
						and (width < 200 and height < 160 or width < 160 or height < 40):
					self.drop(node)
			elif node.tag == 'a' and not node.get('href', '').startswith('http://'):
				self.drop(node)

	def clean_nodes(self):
		children = self.doc.getchildren()
		if len(children) == 1:
			children = children[0].getchildren()

		self.nodes = OrderedDict()

		for child in children:
			if re.search('display: ?none', child.get('style', '')):
				self.drop(child)
				continue
				 
			text = clean(child.text_content() or '')
			text_len = len(text) + len(child.xpath('.//img')) * 10

			if child.tag == 'img':
				text_len += 10

			link_len, links = 0, child.xpath('.//a')
			if len(links) == 1:
				link_text = clean(links[0].text_content() or '')
				if link_text != links[0].get('href'):
					link_len += len(link_text)
			else:
				for link in links:
					link_text = clean(link.text_content() or '')
					link_len += len(link_text)

			node = dict(
				text=text,
				text_len=text_len,
				link=len(links),
				link_len=link_len,
				density=float(link_len) / text_len if text_len else 0,
				drop=False,
			)
			self.nodes[child] = node

			if node['link'] >= 2 and node['density'] >= 0.3 \
					or node['link'] >= 5 and node['density'] >= 0.25 \
					or node['link'] >= 8 and node['density'] >= 0.18 \
					or node['link'] >= 12 and node['density'] >= 0.12 \
					or node['link'] >= 20 \
					or BADS.search(text) and node['text_len'] < 300 \
					or (self.title in node['text'] and (node['text_len'] < 60 
							or child.xpath('.//h1|.//h2|.//h3|.//h4|.//h5|.//h6')
							or 'title' in child.get('class', '').lower()
							or 'title' in child.get('id', '').lower()
					)) or child.tag in BLOCKS and node['text_len'] < 2:
				self.drop(child)
				node['drop'] = True

		needs, drop = [], False
		for child, node in self.nodes.iteritems():
			if drop == True:
				if node['drop'] == False:
					if node['text_len'] - node['link_len'] <= 40:
						if child.xpath('//h1|//h2|//h3|//h4|//h5|//h6'):
							continue
						needs.append(child)
					else:
						needs, drop = [], False
				else:
					for child in needs:
						self.drop(child)
					needs = []
			elif node['drop'] == True:
				drop = True

		for child in needs:
			self.drop(child)

	def clean_tags(self):
		for link in self.doc.xpath('.//a'):
			if clean(link.text_content() or '') != link.get('href'):
				link.drop_tag()

		skips = 'b|strong|big|small|img|a|pre|code|br|thead|tfoot|tr|th|td'.split('|')
		for node in self.doc.iter():
			if node.tag not in BLOCKS and node.tag not in skips:
				node.drop_tag()

	def clean(self):
		return Marker(self.title, self.doc).content

	def clean_texts(self, html):
		doc = clean_html(html, return_doc=True)
		html = ''
		for child in doc.getchildren():
			if child.getchildren():
				html += doc2html(child)
				continue
			text = child.text_content() or ''
			text = self.clean_text(text.strip())
			if text:
				child.text = text
				html += doc2html(child)
		return html

	def clean_text(self, text):
		texts = []
		bads = re.compile(u'记者|摄|请私信|图片来源')
		for text in text.split(u'。'):
			text = text.strip()
			if text and text not in self.texts and not bads.search(text):
				self.texts.add(text)
				texts.append(text)
		return u'。'.join(texts) + u'。' if len(texts) else ''

	def drop(self, node):
		if self.debug:
			node.attrib['drop'] = 'true'
		else:
			node.drop_tree()

	def drop_text(self, node):
		if node.text:
			if self.debug:
				node.text = '{{ ' + node.text + ' }}'
			else:
				node.text = ''

	def drop_tail(self, node):
		if node.tail:
			if self.debug:
				node.tail = '{{ ' + node.tail + ' }}'
			else:
				node.tail = ''


def to_int(x):
	if not x or not x.strip():
		return None
	x = x.strip()
	if x.endswith('px'):
		return int(x[:-2])
	if x.endswith('em'):
		return int(x[:-2]) * 12
	if x[-1] not in '0123456789':
		return None
	return int(x)


def clean(text):
	text = re.sub('\s*\n\s*', '\n', text)
	text = re.sub('[ \t]{2,}', ' ', text)
	return text.strip()


def text_length(i):
	return len(clean(i.text_content() or ""))


def clean_content(html, **options):
	return Cleaner(html, **options).content