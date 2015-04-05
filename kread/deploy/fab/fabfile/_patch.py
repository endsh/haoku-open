# coding: utf-8
from patch import ups, downs
from fabric.api import cd, lcd
from fabric.api import run, local, get, put, execute, hosts

__all__ = [
	'pl', 'pr', 'plr', 'prl', 'up1213', 'up1213_cmd',
]

ldata = '/home/linshao/svn/kread/data/patch/'
rdata = '/home/kread/checkouts/haoku.net/data/patch/'


def pl(cmd, *args):
	module = 'patch.%s' % cmd
	local('python -m %s local %s' % (module, ' '.join(args)))

	__import__('patch.%s' % cmd)

	for up in ups():
		put(ldata + up, rdata + up)


def pr(cmd, *args):
	with lcd('/home/linshao/svn/kread'):
		local('svn commit -m auto-commit')

	with cd('/home/kread/checkouts/haoku.net'):
		run('svn update')

	module = 'patch.%s' % cmd

	if args and args[0] == 'nohup':
		log = '-'.join(args) + '.log'
		args = args[1:]
		run('nohup /home/kread/bin/python -m %s remote %s > %s 2>&1 &' % (module, ' '.join(args), log))
	else:
		run('/home/kread/bin/python -m %s remote %s' % (module, ' '.join(args)))

	__import__('patch.%s' % cmd)

	for down in downs():
		get(rdata + down, ldata + down)


def plr(cmd, *args):
	pl(cmd, *args)
	pr(cmd, *args)


def prl(cmd, *args):
	pr(cmd, *args)
	pl(cmd, *args)


def up1213(start=0):
	start = int(start)
	start = start * 22
	execute(up1213_haoku, start, 3)
	execute(up1213_coolnote, start + 3, 3)
	execute(up1213_haocool, start + 6, 7)
	execute(up1213_chiki, start + 13, 3)
	execute(up1213_formatter, start + 16, 3)
	execute(up1213_51ku, start + 19, 3)


@hosts('kread@haoku.net')
def up1213_haoku(start, count):
	up1213_all(start, count)


@hosts('kread@coolnote.cn')
def up1213_coolnote(start, count):
	up1213_all(start, count)


@hosts('kread@haocool.net')
def up1213_haocool(start, count):
	up1213_all(start, count)


@hosts('kread@chiki.org')
def up1213_chiki(start, count):
	up1213_all(start, count)


@hosts('kread@formatter.org')
def up1213_formatter(start, count):
	up1213_all(start, count)


@hosts('kread@51ku.net')
def up1213_51ku(start, count):
	up1213_all(start, count)


def up1213_all(start, count):
	with cd('~/checkouts/haoku.net'):
		for x in range(start, start + count):
			up1213_cmd(x)


def up1213_cmd(num=0):
	run('$(nohup ~/bin/python -m patch.spider_20141209 remote %d 12 > bw-%d.log 2>&1 &) && sleep 1' % (num * 12, num))