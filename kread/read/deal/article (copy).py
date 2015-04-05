# coding: utf-8
import re
from deal.clean import clean_content
from utils import clean_html, clean_html, doc2html, html2doc, html2text
from utils import chinese_count, get_domain, url2filetype
from utils import fetch_urls, get_or_cache

__all__ = [
	'ArticleExtractor', 'ArticleMerger', 'html2article',
]


BLOCK_TAGS = ['div','p','table','td','article','section','pre']
BLOCK_XPATH = '|'.join(['.//%s' % x for x in BLOCK_TAGS])
REGEXES = {
	'time': re.compile(u'(((19|20)\d{2})([-\./]|年)([01]?\d)([-\./]|月)([0-3]?\d)日?)[ ,]*(([0-2]?\d):([0-6]\d)(:([0-6]\d))?)?'),
	'positive': re.compile('article|body|content|entry|hentry|main|page|pagination|post|text|blog|story', re.I),
	'negative': re.compile('combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget', re.I),
}


class ArticleExtractor(object):

	def __init__(self, input, url, **options):
		self.input = input
		self.url = url
		self.options = options
		if 'title' in options:
			self._title = options.get('title')
		if 'pages' in options:
			self._pages = options.get('pages')

		self.doc = clean_html(input, url, return_doc=True)
		self.html = doc2html(self.doc)

	def get_block_text(self, node, default=''):
		if node.xpath(BLOCK_XPATH):
			return default
		text = ''
		for child in node.iter():
			if child.text:
				text += child.text.strip()
			if child != node and child.tail:
				text += child.tail.strip()
		return text

	def get_next_text(self, node, default_text='', default_link=''):
		link = ''
		for sib in node.itersiblings():
			for child in sib.iter():
				if child.text and child.text.strip():
					if child.tag == 'a':
						link = child.get('href', '')
					return link, child.text.strip()
				if child.tail and child.tail.strip():
					return link, child.tail.strip()
		return default_link, default_text

	def get_selector(self, node):
		if node is not None:
			path = str(node.tag)
			if node.get('id') and not re.search('\d{2,}', node.get('id')):
				return '%s#%s' % (path, node.get('id'))
			if node.get('class') and not re.search('\d{2,}', node.get('class')):
				path = '%s.%s' % (path, '.'.join(node.get('class').split()))
			if node.getparent() is not None:
				return '%s > %s' % (self.get_selector(node.getparent()), path)
			return path

	@property
	def title(self):
		if not hasattr(self, '_title'):
			self._title = self.xtitle['text']
		return self._title

	@property
	def xtitle(self):
		if not hasattr(self, '_xtitle'):
			self._xtitle = self._parse_title()
		return self._xtitle

	def _parse_title(self):
		title = self.doc.find('.//title')
		if title is None or not title.text or not title.text.strip():
			return self.node2title()
		title = title.text.strip()

		if 'title_selector' in self.options and self.options['title_selector']:
			heads = []
			for node in self.doc.cssselect(self.options['title_selector']):
				text = self.get_block_text(node)
				if text and (title.startswith(text) or title.endswith(text)):
					heads.append(node)
			if len(heads) == 1:
				return self.node2title(heads[0], title)

		heads = []
		for node in self.doc.iter('h1'):
			text = self.get_block_text(node)
			if text and (title.startswith(text) or title.endswith(text)):
				heads.append(node)
		if len(heads) == 1:
			return self.node2title(heads[0], title)

		maxlen, node = 0, None
		for child in self.doc.find('body').iter():
			if child.text and child.text.strip():
				text = child.text.strip()
				if len(text) >= maxlen and (title.startswith(text) or title.endswith(text)):
					if len(text) > maxlen or child.tag in 'h1|h2|h3|h4|h5|h6':
						maxlen, node = len(text), child
			if child.tail and child.tail.strip() and child.getparent() is not None:
				text = child.tail.strip()
				if len(text) > maxlen and (title.startswith(text) or title.endswith(text)):
					if len(text) > maxlen or child.getparent().tag in 'h1|h2|h3|h4|h5|h6':
						maxlen, node = len(text), child.getparent()
		return self.node2title(node, title)

	def node2title(self, node=None, title=''):
		res = {'text':'', 'selector':'', 'node':None}
		if node is None or title == '':
			return res

		res['node'] = node
		res['selector'] = self.get_selector(node)
		text = self.get_block_text(node)
		if text and text in title:
			res['text'] = text
			return res

		maxlen = 0
		for child in node.iter():
			if child.text and child.text.strip():
				text = child.text.strip()
				if len(text) >= maxlen and (title.startswith(text) or title.endswith(text)):
					maxlen, res['text'] = len(text), text
			if child.tail and child.tail.strip():
				text = child.tail.strip()
				if len(text) >= maxlen and (title.startswith(text) or title.endswith(text)):
					maxlen, res['text'] = len(text), text
		return res

	@property
	def content(self):
		if not hasattr(self, '_content'):
			self._content = self.xcontent['text']
		return self._content

	@property
	def xcontent(self):
		if not hasattr(self, '_xcontent'):
			self._xcontent = self._parse_content()
		return self._xcontent

	def _parse_content(self):
		node, score = self.get_content_node()
		return self.node2content(node, score)

	def get_content_node(self):
		node, score = None, 0
		if 'content_selector' in self.options and self.options['content_selector']:
			node, score = self.get_best_node(
				self.doc.cssselect(self.options['content_selector']))
			# print self.options['content_selector']
			# print node
			# return node, score
		if node is None:
			node, score = self.get_best_node(self.doc.iter())
		return node, score

	def get_best_node(self, nodes):
		scores = {}
		for node in nodes:
			scores[node] = self.get_score(node)
		if scores:
			return max(scores.iteritems(), key=lambda x: x[1])
		return None, 0

	def get_score(self, node):
		score = self.class_score(node)
		score += self.tag_score(node)
		score += self.children_score(node)
		return score

	def class_score(self, node):
		score = 0
		for feature in [node.get('class', None), node.get('id', None)]:
			if feature:
				if REGEXES['negative'].search(feature):
					score -= 25
				elif REGEXES['positive']:
					score += 25
		return score

	def tag_score(self, node):
		scores = [
			(['div'], 20),
			(['pre', 'td', 'blockquote'], 5),
			(['address', 'ol', 'ul', 'dl', 'dd', 'dt', 'li', 'form'], -5),
			(['h1', 'h3', 'h3', 'h4', 'h5', 'h6'], -10),
		]
		tag = str(node.tag).lower()
		for tags, score in scores:
			if tag in tags:
				return score
		return 0

	def children_score(self, node):
		score = 0
		for child in node.getchildren():
			if child.get('id'): 
				score -= 10
			elif child.tag in ['p', 'pre', 'code']:
				if not child.xpath(BLOCK_XPATH):
					score += 20
			elif child.get('class'):
				score -= 5
			score += len(child.xpath('/br'))
			text = child.text_content()
			chineses = chinese_count(text)
			symbols = len(re.findall(u'(，|。)+', text))
			if symbols > 0 and chineses / symbols > 5:
				score += symbols * 5 + chineses * 0.1
		return score

	def node2content(self, node, score):
		res = {'text':'', 'selector':'', 'score':0, 'node':None}
		if node is None or score < 50:
			return res

		res['node'] = node
		res['score'] = score
		res['selector'] = self.get_selector(node)

		options = {}
		if 'texts' in self.options:
			options['texts'] = self.options['texts']
		if 'debug' in self.options:
			options['debug'] = self.options['debug']
		res['text'] = clean_content(
			doc2html(node),
			url=self.url,
			title=self.title,
			pages=self.pages,
			**options
		)
		return res

	@property
	def pages(self):
		if not hasattr(self, '_pages'):
			self._pages = self.get_pages()
		return self._pages

	def get_pages(self):
		file_type = url2filetype(self.url)
		if not file_type:
			return []
		pages = set([self.url])
		prefix = self.url[:-len(file_type) - 1]
		if re.match('.*[_\-]\d$', prefix):
			prefix = self.url[:-len(file_type) - 3]
		prefix_len = len(prefix)

		for node in self.doc.iter('a'):
			href = node.get('href').strip() if node.get('href') else None
			if href and len(href) > prefix_len + 2 \
					and href[:prefix_len] == prefix:
				href = href.split('#')[0].split('?')[0]
				pages.add(href)

		if len(pages) > 1:
			return list(pages)
		return []

	@property
	def source(self):
		if not hasattr(self, '_source'):
			self._source = self.xsource['text']
		return self._source

	@property
	def xsource(self):
		if not hasattr(self, '_xsource'):
			self._xsource = self._parse_source()
		return self._xsource

	def _parse_source(self):
		node = self.get_source_node()
		return self.node2source(node)		

	def get_source_node(self):
		if 'source_selector' in self.options:
			if self.options['source_selector']:
				nodes = self.doc.cssselect(self.options['source_selector'])
				if len(nodes) == 1:
					return nodes[0]
				for node in nodes:
					res = self.has_source(node)
					if res is not None:
						return res

		for node in self.doc.find('body').iter():
			res = self.has_source(node)
			if res is not None:
				return res

		domain = get_domain(self.url)
		for a in self.doc.iter('a'):
			link = a.get('href')
			if link and link.startswith('http') \
					and get_domain(link) != domain:
				text = self.get_block_text(a)
				if len(text) > 2 \
						and text.endswith(u'报') \
						and not text.endswith(u'举报'):
					return a

	def has_source(self, node):
		if node.text and node.text.strip():
			text = node.text.strip()
			if text and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
				return node
		if node.tail and node.tail.strip():
			text = node.tail.strip()
			if text and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
				return node

	def node2source(self, node):
		res = {'text':'', 'link':'', 'selector':'', 'node':node}
		if node is None:
			return res

		res['selector'] = self.get_selector(node)
		link = ''
		text = node.text.strip() if node.text else ''
		tail = node.tail.strip() if node.tail else ''
		if text and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
			text = text[text.index(u'源') + 2:].strip()
			if not text:
				for child in node.iter():
					if child == node:
						continue
					if child.text and child.text.strip():
						text = child.text.strip()
						if child.tag == 'a':
							link = child.get('href', '')
						break
					if child.tail and child.tail.strip():
						text = child.tail.strip()
						break
				if not text:
					text = tail
					if not text:
						link, text = self.get_next_text(node)
			text = text.split('|')[0] if text else ''
			text = text.split()[0] if text else ''
		elif tail and re.search(u'(?!(图片|视频))[稿来]源[：:]', text):
			text = text[tail.index(u'源') + 2:].strip()
			if not text:
				link, text = self.get_next_text(node)
			text = text.split('|')[0] if text else ''
			text = text.split()[0] if text else ''
		else:
			link, text = node.get('href', ''), self.get_block_text(node)

		if len(text) < 16 and not REGEXES['time'].search(text):
			res['link'], res['text'] = link, text
		return res

	@property
	def pubtime(self):
		if not hasattr(self, '_pubtime'):
			self._pubtime = self._parse_pubtime()
		return self._pubtime

	def _parse_pubtime(self):
		dates = REGEXES['time'].findall(self.html)
		if not dates:
			return ''

		for _,year,_,_,month,_,date,_,hour,minute,_,second in dates:
			if minute:
				date = '%4d-%02d-%02d %02d:%02d' % (
					int(year), int(month), int(date), int(hour), int(minute))
				if second:
					date = '%s:%02d' % (date, int(second))
				return date

		return '%4d-%02d-%02d' % (
					int(dates[0][1]), int(dates[0][4]), int(dates[0][6]))

	@property
	def imgs(self):
		if not hasattr(self, '_imgs'):
			self._imgs = self._parse_imgs()
		return self._imgs

	def _parse_imgs(self):
		imgs = set()
		doc = html2doc(self.content)
		for img in doc.iter('img'):
			src = img.get('src')
			if src and src.strip():
				imgs.add(src.strip())
		return list(imgs)

	@property
	def article(self):
		score = len(html2text(self.content)) + len(self.imgs) * 50
		if len(self.title) < 4 or score < 100:
			return None
		return {
			'title':self.title,
			'content':self.content,
			'src_name':self.xsource['text'],
			'src_link':self.xsource['link'],
			'pubtime':self.pubtime,
			'pages':self.pages,
			'imgs':self.imgs,
		}

	@property
	def selector(self):
		return {
			'title_selector':self.xtitle['selector'],
			'content_selector':self.xcontent['selector'],
			'source_selector':self.xsource['selector'],
		}


class ArticleMerger(object):

	def __init__(self, url, title, htmls, **options):
		self.url = url
		self.title = title
		self.htmls = htmls
		self.options = options
		self.pages = self.sort(htmls.keys())

	def sort(self, pages):
		file_type = url2filetype(self.url) or ''

		prefix = self.url[:-len(file_type) - 1]
		if re.match('[_\-]\d$', prefix):
			prefix = self.url[:-len(file_type) - 3]
		prefix_len = len(prefix)

		res = {}
		for url in pages:
			num = re.search('\d+', url[prefix_len:-len(file_type) - 1])
			res[url] = int(num.group(0)) if num else 0

		return [x[0] for x in sorted(res.iteritems(), key=lambda x: x[1])]

	@property
	def content(self):
		if not hasattr(self, '_content'):
			self._content = self._merge_content()
		return self._content

	def _merge_content(self):
		content = ''
		options = self.options
		options['title'] = self.title
		options['pages'] = self.pages
		options['texts'] = set()
		for url in self.pages:
			content += ArticleExtractor(self.htmls[url], url, **options).content
		return content

	@property
	def imgs(self):
		if not hasattr(self, '_imgs'):
			self._imgs = self._parse_imgs()
		return self._imgs

	def _parse_imgs(self):
		imgs = set()
		doc = html2doc(self.content)
		for img in doc.iter('img'):
			src = img.get('src')
			if src and src.strip():
				imgs.add(src.strip())
		return list(imgs)


def html2article(html, url, selector=False, merge=False, **options):
	extractor = ArticleExtractor(html, url, **options)
	article = extractor.article
	if article is not None and selector:
		article.update(extractor.selector)

	if article is not None and article['pages'] and merge:
		article['content'] = ArticleMerger(
			url,
			extractor.title, 
			fetch_urls(extractor.pages, handle=get_or_cache),
			**extractor.selector
		).content
	return article