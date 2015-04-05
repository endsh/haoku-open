# coding: utf-8
import re

__all__ = {
	'selector',
}


def selector(node):
	if node is not None:
		path = str(node.tag)
		if node.get('id') and not re.search('\d{2,}', node.get('id')):
			return '%s#%s' % (path, node.get('id'))
		if node.get('id') and not re.search('\d{2,}', node.get('class')):
			path = '%s.%s' % (path, '.'.join(node.get('class').split()))
		if node.getparent() is not None:
			return '%s > %s' % (selector(node.getparent()), path)
		return path
	return ''