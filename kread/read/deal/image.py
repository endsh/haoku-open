# coding: utf-8
import conf
from PIL import Image
from cStringIO import StringIO
from utils import html2doc, doc2html, child2html

__all__ = [
	'content4imgs', 'img2size', 'img2link',
]


def content4imgs(content, title, imgs):
	doc = html2doc(content)
	bads = []
	for img in doc.iter('img'):
		src = img.get('src')
		if src in imgs:
			if imgs[src]['count'] >= 10 \
					or imgs[src]['count'] >= 5 and (imgs[src]['width'] < 240 or imgs[src]['height'] < 160) \
					or imgs[src]['count'] >= 2 and (imgs[src]['width'] < 200 or imgs[src]['height'] < 120) \
					or imgs[src]['width'] < 160 or imgs[src]['height'] < 40 \
					or imgs[src]['width'] < 360 and -10 < imgs[src]['width'] - imgs[src]['height'] < 10:
				parent = img.getparent()
				if parent is not None and parent.get('class') == 'article-img':
					parent.drop_tree()
				else:
					img.drop_tree()
				bads.append(imgs[src]['md5'])
			else:
				img.attrib['src'] = img2link(imgs[src]['path'])
	return bads, child2html(doc)


def img2link(path):
	if conf.RELEASE:
		return 'http://img.haoku.net/%s@95Q.jpg' % path
	else:
		return '/img/%s' % path


def img2size(data):
	img = Image.open(StringIO(data))
	return img.size


def main():
	from utils import load_data, atime
	print atime('test')(img2size)(load_data('test.png'))


if __name__ == '__main__':
	main()