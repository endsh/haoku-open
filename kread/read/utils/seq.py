#-*- coding: utf8 -*-

# base data
word = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
seq = (9,5,1,0,4,8,7,3,2,6)
base = (
	(1,10),
	(10,1,100),
	(100,1,10,1000),
	(1000,1,100,10,10000),
	(10000,1,10,1000,100,100000),
	(100000,10,1,10000,1000,100,1000000),
	(1000000,100,1,10000,100000,10,1000,10000000),
	(10000000,1000,1,10000,1000000,100,10,100000,100000000),
	(100000000,10000,1,10,100000,10000000,1000,100,1000000,1000000000),
	(1000000000,100000,10,1,10000,100000000,10000000,1000,100,1000000,10000000000),
)


def seq10(num, m=10, offset=11111, times=40):
	res = num
	for i in range(times):
		num = 0
		for j in range(m):
			num += seq[res % 10] * base[m - 1][j]
			res /= 10
		res = (num + offset + i) % base[m - 1][m]
	return res


def seqw(num):
	num = seq10(num)
	res = ''
	while num > 0:
		res += word[num % 62]
		num /= 62
	return res
