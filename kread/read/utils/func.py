# coding: utf-8

__all__ = ["rename"]


def rename(name):
	def wrapper(func):
		func.__name__ = name
		return func
	return wrapper
