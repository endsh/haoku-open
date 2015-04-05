# coding: utf-8
from utils import load_json
from .base import spider
from .cmd import *


@local()
def handle_tpls():
	tpls = load_json('spider/tpls.json')
	for tpl in tpls.itervalues():
		spider.template.save(tpl)


if __name__ == '__main__':
	main()
