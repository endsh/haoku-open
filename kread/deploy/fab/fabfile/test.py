# coding: utf-8
from fabric.api import cd, env, put, run, sudo, hosts


@hosts('test@haoku.net')
def test_upweb():
	test_setup_web()
	test_setup_env()


def test_setup_web():
	put('test/web.test.xml', '/home/test/etc/web.test.xml')
	put('test/api.v1.test.xml', '/home/test/etc/api.v1.test.xml')
	put('test/accounts.test.xml', '/home/test/etc/accounts.test.xml')
	put('test/accounts.api.v1.test.xml', '/home/test/etc/accounts.api.v1.test.xml')


def test_setup_env():
	put('test/bash_profile', '/home/test/.bash_profile')


@hosts('test@haoku.net')
def test_uwsgi_reload():
	run('HAOKU_TEST=TEST ~/bin/uwsgi --reload ~/run/accounts.api.v1.test.pid')
	run('HAOKU_TEST=TEST ~/bin/uwsgi --reload ~/run/accounts.test.pid')
	run('HAOKU_TEST=TEST ~/bin/uwsgi --reload ~/run/api.v1.test.pid')
	run('HAOKU_TEST=TEST ~/bin/uwsgi --reload ~/run/web.test.pid')


@hosts('test@haoku.net')
def test_uwsgi_start():
	run('HAOKU_TEST=TEST ~/bin/uwsgi ~/etc/accounts.api.v1.test.xml')
	run('HAOKU_TEST=TEST ~/bin/uwsgi ~/etc/accounts.test.xml')
	run('HAOKU_TEST=TEST ~/bin/uwsgi ~/etc/api.v1.test.xml')
	run('HAOKU_TEST=TEST ~/bin/uwsgi ~/etc/web.test.xml')


@hosts('test@haoku.net')
def test_uwsgi_stop():
	run('HAOKU_TEST=TEST ~/bin/uwsgi --stop ~/run/accounts.api.v1.test.pid')
	run('HAOKU_TEST=TEST ~/bin/uwsgi --stop ~/run/accounts.test.pid')
	run('HAOKU_TEST=TEST ~/bin/uwsgi --stop ~/run/api.v1.test.pid')
	run('HAOKU_TEST=TEST ~/bin/uwsgi --stop ~/run/web.test.pid')
