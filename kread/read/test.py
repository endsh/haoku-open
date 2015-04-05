# coding: utf-8
import requests
from utils import cache_key, html2doc


def unicode(s):
    encodings = ["utf-8", "gb18030", "gb2312", "gbk", "big5", "ascii"]
    for enc in encodings:
        try:
            print s
            utf8 = s.decode(enc, 'ignore').encode('utf-8')
            try:
                html2doc(utf8)
            except Exception, e:
                print e.__class__.__name__
                continue
            return enc
        except UnicodeDecodeError, e:
            print str(e)
            pass
    print 'unknown'


def test_url(url):
    print url, unicode(requests.get(url).content)


def main():
    urls = """http://travel.sina.com.cn/shouer_2726-xiangqing-gonglue/""".splitlines()
    for url in urls:
        test_url(url)


if __name__ == '__main__':
    main()