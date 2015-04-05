# coding: utf-8
from utils import load_json, save_json

__all__ = [
	"get_test_urls", "save_test_urls", "clean_test_urls",
	"add_test_url",
]


def add_test_url(url):
	urls = get_test_urls()
	if url not in urls:
		urls.append(url)
		save_test_urls(urls)


def get_test_urls():
	return load_json('test-history.urls') or []


def save_test_urls(urls):
	save_json('test-history.urls', urls)


def clean_test_urls():
	save_json('test-history.urls', [])
