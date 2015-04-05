#-*- coding: utf8 -*-
import os
import fabtools
from fabric.api import cd, lcd, env, put, run, sudo
from fabric.api import hosts, roles, local, execute
from ._patch import *
from ._spider import *
from ._mongo import *
from .nginx import *
from .test import *

cwd = os.getcwd()
all_users = ['kread']
required_dirs = ['checkouts', 'etc', 'log', 'run']

haoku_ip = 'need ip address'
haocool_ip = 'need ip address'
ku51_ip = 'need ip address'
chiki_ip = 'need ip address'
formatter_ip = 'need ip address'
coolnote_ip = 'need ip address'


env.roledefs = {
	'all': [
		'kread@haoku.net',
		'kread@coolnote.cn',
		'kread@chiki.org',
		'kread@haocool.net',
		'kread@51ku.net',
		'kread@formatter.org',
	],
	'root': [
		'root@haoku.net',
		'root@coolnote.cn',
		'root@chiki.org',
		'root@haocool.net',
		'root@51ku.net',
		'root@formatter.org',
	],
}

def test():
	users('test')
	checkout('test')
	execute(test_upweb)


def all():
	install_packages('build')
	install_packages('web')
	users('kread')
	checkout('kread')
	setup_env('kread')
	host_file()


def build():
	install_packages('build')
	install_packages('web')
	users('kread')


def iread():
	checkout('kread')
	setup_env('kread')


def web():
	setup_web('kread')


def install_packages(type=None):
	sudo('apt-get update')
	sudo('apt-get install -y vim software-properties-common')
	sudo('apt-get install -y python-setuptools')
	sudo('easy_install pip')
	sudo('pip install -U virtualenv')

	if type == 'build':
		sudo(
			' apt-get install -y python-dev subversion curl libxml2-dev libxslt1-dev'
			' libevent-dev libmysqlclient-dev git g++ unzip'
		)

	if type == 'web':
		sudo('apt-get install -y nginx python-dev libxml2-dev libxslt1-dev libpcre3 libpcre3-dev')


def users(user=None):
	users = [user] if user else all_users
	for user in users:
		home = '/root' if user == 'root' else '/home/%s' % user
		if not fabtools.user.exists(user):
			sudo('adduser --gecos "" -q --disabled-password %s' % user)

		if not fabtools.files.is_file('%s/.ssh/authorized_keys' % home):
			sudo('mkdir -p %s/.ssh' % home)
			put('keys/*.pub', '%s/.ssh/authorized_keys' % home, mode=700, 
				use_sudo=True)
			sudo('chown -R %s:%s %s' % (user, user, home))
			sudo('chmod -R 700 %s' % home)


def checkout(user=None):
	users = [user] if user else all_users
	for user in users:
		env.user = user
		home = '/home/%s' % user
		for dir in required_dirs:
			run('mkdir -p %s/%s' % (home, dir))
		if not fabtools.files.is_dir('%s/checkouts/haoku.net' % home):
			with cd('%s/checkouts' % home):
				run('svn co svn://coolnote.cn/kread haoku.net')
		else:
			with cd('%s/checkouts/haoku.net' % home):
				run('svn update')

		if not fabtools.files.is_dir('%s/checkouts/simin' % home):
			with cd('%s/checkouts' % home):
				run('svn co svn://coolnote.cn/simin simin')
		else:
			with cd('%s/checkouts/simin' % home):
				run('svn update')

		if not fabtools.files.is_dir('%s/bin/python' % home):
			run('virtualenv %s' % home)
		run(('%s/bin/pip install -r %s/checkouts/haoku.net/'
			'deploy_requirements.txt --index-url=http://pypi.douban.com/simple/') % (home, home))

		with cd(home):
			run('scp root@coolnote.cn:/home/kread/oss.zip .')
			run('unzip oss.zip -d oss')
			run('%s/bin/python %s/oss/setup.py install' % (home, home))
	
		sudo('chown -R %s:%s %s' % (user, user, home))
		sudo('chmod -R 700 %s' % home)


@roles('all')
def up141115(user=None):
	users = [user] if user else all_users
	for user in users:
		env.user = user
		home = '/home/%s' % user
		if not fabtools.files.is_dir('%s/checkouts/simin' % home):
			with cd('%s/checkouts' % home):
				run('svn co svn://coolnote.cn/simin simin')
		else:
			with cd('%s/checkouts/simin' % home):
				run('svn update')
	execute(setup_env)


def setup_env(user=None):
	users = [user] if user else all_users
	for user in users:
		env.user = user
		home = '/home/%s' % user
		put('files/bash_profile', '%s/.bash_profile' % home)


def setup_web(user=None):
	home = '/home/%s' % user
	put('files/later.xml', '%s/etc/later.xml' % home)


def host_file():
	host_string = """
%s haoku.net
%s haocool.net
%s 51ku.net
%s chiki.org
%s formatter.org
%s coolnote.cn
	""" % (haoku_ip, haocool_ip, ku51_ip, chiki_ip, formatter_ip, coolnote_ip)
	sudo("echo '%s' >> /etc/hosts " % host_string)


def sysrc():
	with lcd('/home/linshao/svn/kread'):
		local('svn commit -m auto-commit')
	execute(upsrc)


@roles('all')
def upsrc():
	with cd('/home/kread/checkouts/haoku.net'):
		run('svn update')


@hosts('kread@haoku.net')
def clear():
	local('/home/linshao/cmd/oss/osscmd deleteallobject oss://hkhtml/')
	local('/home/linshao/cmd/oss/osscmd deleteallobject oss://hkimg/')
	with cd('/home/kread/checkouts/haoku.net'):
		run('/home/kread/bin/python read/tool/best2spider.py')


@roles('all')
def cmd(c):
	run(c)


@roles('root')
def root_cmd(c):
	run(c)


def do(c):
	run(c)
