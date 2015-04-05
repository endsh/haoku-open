#!python
# coding: utf-8
import sys


def main():
	if len(sys.argv) >= 2:
		module = __import__(sys.argv[1])
		for sub in sys.argv[1].split('.')[1:]:
			module = getattr(module, sub)

		module.app.run(
			host='0.0.0.0',
			port=module.app.config.get('APPID', 5000),
		)


if __name__ == '__main__':
	main()