# coding: utf-8
from collections import defaultdict
from utils import get_or_cache, get_chinese, get_test_urls
from utils import save_json, print_dict


def ichinese():
	urls = get_test_urls()
	res = defaultdict(int)
	for url in urls:
		html = get_or_cache(url)
		chs = get_chinese(html)
		for ch in chs:
			res[ch] += 1

	res = '|'.join([a for a, b in sorted(filter(lambda x: x[1] >= 40, res.iteritems()), key=lambda x: -x[1])])
	save_json('chineses.json', res)


if __name__ == '__main__':
	ichinese()