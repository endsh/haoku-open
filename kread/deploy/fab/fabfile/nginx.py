# coding: utf-8
from fabric.api import cd, env, put, run, sudo, hosts


@hosts('kread@haoku.net')
def upweb():
	setup_web()
	setup_env()


def nginx():
	nginx_config()
	nginx_reload()


def nginx_config():
	put('../nginx/later.nginx.conf', '/etc/nginx/sites-enabled/later')
	put('../nginx/dash.nginx.conf', '/etc/nginx/sites-enabled/dash')
	put('../nginx/test.nginx.conf', '/etc/nginx/sites-enabled/test')
	put('../nginx/read.nginx.conf', '/etc/nginx/sites-enabled/read')

	
def nginx_reload():
	sudo('/etc/init.d/nginx reload')


def setup_web():
	put('release/later.xml', '/home/kread/etc/later.xml')
	put('release/dash.xml', '/home/kread/etc/dash.xml')
	put('release/web.xml', '/home/kread/etc/web.xml')
	put('release/api.v1.xml', '/home/kread/etc/api.v1.xml')
	put('release/accounts.xml', '/home/kread/etc/accounts.xml')
	put('release/accounts.api.v1.xml', '/home/kread/etc/accounts.api.v1.xml')


def setup_env():
	put('release/bash_profile', '/home/kread/.bash_profile')


@hosts('kread@haoku.net')
def uwsgi_reload():
	run('~/bin/uwsgi --reload ~/run/accounts.api.v1.pid')
	run('~/bin/uwsgi --reload ~/run/accounts.pid')
	run('~/bin/uwsgi --reload ~/run/api.v1.pid')
	run('~/bin/uwsgi --reload ~/run/web.pid')


@hosts('kread@haoku.net')
def uwsgi_start():
	run('~/bin/uwsgi ~/etc/accounts.api.v1.xml')
	run('~/bin/uwsgi ~/etc/accounts.xml')
	run('~/bin/uwsgi ~/etc/api.v1.xml')
	run('~/bin/uwsgi ~/etc/web.xml')


@hosts('kread@haoku.net')
def uwsgi_stop():
	run('~/bin/uwsgi --stop ~/run/accounts.api.v1.pid')
	run('~/bin/uwsgi --stop ~/run/accounts.pid')
	run('~/bin/uwsgi --stop ~/run/api.v1.pid')
	run('~/bin/uwsgi --stop ~/run/web.pid')
