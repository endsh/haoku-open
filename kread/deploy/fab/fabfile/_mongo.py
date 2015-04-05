# coding: utf-8
from fabric.api import cd, env, put, run, sudo
from fabric.api import hosts, roles, local, execute
from fabric.contrib.files import upload_template

env.password = 'need password'


@hosts('root@haoku.net', 'root@haocool.net', 'root@coolnote.cn', 'root@51ku.net')
def mongos_start():
	with cd('/data2/soft/mongodb'):
		run('bin/mongos -f etc/mongos.conf --fork')


@hosts('root@haoku.net', 'root@haocool.net', 'root@coolnote.cn', 'root@51ku.net')
def mongos_stop():
	run('kill -s 15 `cat /data2/mongos/mongos.pid`')


def mongos_restart():
	execute(mongos_stop)
	execute(mongos_start)


@hosts('root@haoku.net', 'root@haocool.net', 'root@coolnote.cn')
def config_start():
	with cd('/data2/soft/mongodb'):
		run('bin/mongod -f etc/config.conf --fork')


@hosts('root@haoku.net', 'root@haocool.net', 'root@coolnote.cn')
def config_stop():
	run('kill -s 15 `cat /data2/config/config.pid`')


def config_restart():
	execute(config_stop)
	execute(config_start)


@hosts('root@haocool.net', 'root@chiki.org', 'root@formatter.org', 'root@coolnote.cn', 'root@51ku.net')
def mongo_start():
	with cd('/data2/soft/mongodb'):
		run('bin/mongod -f etc/web1.conf --fork')
		run('bin/mongod -f etc/web2.conf --fork')


def mongo_stop():
	execute(_mongo_stop)
	execute(coolnote_mongo_stop)


@hosts('root@haocool.net', 'root@chiki.org', 'root@formatter.org', 'root@51ku.net')
def _mongo_stop():
	run('kill -s 15 `cat /data1/web/mongo.pid`')
	run('kill -s 15 `cat /data2/web/mongo.pid`')


@hosts('root@coolnote.cn')
def coolnote_mongo_stop():
	run('kill -s 15 `cat /data3/web/mongo.pid`')
	run('kill -s 15 `cat /data2/web/mongo.pid`')


def mongo_restart():
	execute(mongo_stop)
	execute(mongo_start)


def recreate_mongo():
	execute(recreate_cluster)
	execute(coolnote_recreate_cluster)


def create_cluster():
	run('mkdir -p /data1/web/data /data1/web/logs')
	run('mkdir -p /data2/web/data /data2/web/logs')
	run('mkdir -p /data2/config/data /data2/config/logs')
	run('mkdir -p /data2/mongos/data /data2/mongos/logs')


def clear_cluster():
	run('rm -rf /data1/web /data2/web /data2/config /data2/mongos')


@hosts('root@haoku.net', 'root@haocool.net', 'root@chiki.org', 'root@formatter.org', 'root@51ku.net')
def recreate_cluster():
	clear_cluster()
	create_cluster()


def coolnote_create_cluster():
	run('mkdir -p /data3/web/data /data3/web/logs')
	run('mkdir -p /data2/web/data /data2/web/logs')
	run('mkdir -p /data2/config/data /data2/config/logs')
	run('mkdir -p /data2/mongos/data /data2/mongos/logs')


def coolnote_clear_cluster():
	run('rm -rf /data3/web /data2/web /data2/config /data2/mongos')


@hosts('root@coolnote.cn')
def coolnote_recreate_cluster():
	coolnote_clear_cluster()
	coolnote_create_cluster()


def mongo():
	run('mkdir -p ~/tar ~/soft ~/data/mongo/data ~/data/mongo/logs')
	run(' -p ~/data/spider/data ~/data/spider/logs')
	put('~/tar/mongodb-linux-x86_64-2.6.3.tgz', '~/tar/mongodb-linux-x86_64-2.6.3.tgz')
	put('~/tar/redis-2.8.12.tar.gz', '~/tar/redis-2.8.12.tar.gz')
	put('~/.bash_profile', '~/.bash_profile')
	run('echo ". ~/.bash_profile" >> ~/.bashrc')

	run('tar zxvf ~/tar/mongodb-linux-x86_64-2.6.3.tgz -C ~/soft')

	run('mkdir -p ~/soft/mongodb-linux-x86_64-2.6.3/etc')
	upload_template('files/mongo.conf',
		'~/soft/mongodb-linux-x86_64-2.6.3/etc/mongo.conf', 
		context={'user':env.user}, use_jinja=True)
	upload_template('files/spider.conf',
		'~/soft/mongodb-linux-x86_64-2.6.3/etc/spider.conf',
		context={'user':env.user}, use_jinja=True)
	
	run('tar zxvf ~/tar/redis-2.8.12.tar.gz -C ~/soft')
	with cd('~/soft/redis-2.8.12'):
		run('make')
