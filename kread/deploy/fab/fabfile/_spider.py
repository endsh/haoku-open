# coding: utf-8
from fabric.api import cd, run, hosts, execute

__all__ = [
	'fetch', 'handle', 'single', 'master', 'worker', 
	'fetchs', 'handles', 'killall', 'redis_stop', 'redis_start',
]


def fetch():
	with cd('/home/kread/checkouts/haoku.net'):
		run('$(nohup /home/kread/bin/python read/spider/fetcher.py > /dev/null 2>&1 &) && sleep 1')


def handle():
	with cd('/home/kread/checkouts/haoku.net'):
		run('$(nohup /home/kread/bin/python read/spider/handler.py > /dev/null 2>&1 &) && sleep 1')


def real_time_handle():
	with cd('/home/kread/checkouts/haoku.net'):
		run('$(nohup /home/kread/bin/python read/spider/handler.py realtime > /dev/null 2>&1 &) && sleep 1')


def seg_handle():
	with cd('/home/kread/checkouts/haoku.net'):
		run('$(nohup /home/kread/bin/python read/spider/handler.py segment > /dev/null 2>&1 &) && sleep 1')


def single():
	fetch()
	handle()


@hosts('kread@haoku.net')
def master():
	with cd('/home/kread/checkouts/haoku.net'):
		run('$(nohup /home/kread/bin/python read/spider/master.py > /dev/null 2>&1 &) && sleep 1')


def worker():
	execute(fetchs)
	execute(haoku)
	execute(handles)
	execute(ext_handles)


@hosts('kread@haoku.net', 'kread@coolnote.cn', 'kread@chiki.org', 
		'kread@formatter.org', 'kread@51ku.net', 'kread@haocool.net')
def fetchs():
	fetch()


@hosts('kread@haoku.net', 'kread@coolnote.cn', 'kread@51ku.net', 'kread@haocool.net')
def haoku():
	seg_handle()


@hosts('kread@chiki.org', 'kread@formatter.org', 'kread@haocool.net', 'kread@haoku.net', 'kread@coolnote.cn', 'kread@51ku.net')
def handles():
	real_time_handle()


@hosts('kread@haocool.net')
def ext_handles():
	seg_handle()
	seg_handle()


@hosts(
	'kread@haoku.net',
	'kread@coolnote.cn',
	'kread@chiki.org',
	'kread@formatter.org',
	'kread@51ku.net',
	'kread@haocool.net',
)
def killall():
	run('killall python')


@hosts('root@chiki.org')
def redis_stop():
	run('service redis_6379 stop')


@hosts('root@chiki.org')
def redis_start():
	run('service redis_6379 start')