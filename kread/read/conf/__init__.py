# coding: utf-8
import os
from .base import *

TEST = True if os.environ.get('HAOKU_TEST') == 'TEST' else False
RELEASE = True if os.environ.get('HAOKU_READ') == 'release' else False
if RELEASE:
	from .release import *


STATUS = 'DEBUG'
if TEST == True:
	STATUS = 'TEST'
elif RELEASE == True:
	STATUS = 'RELEASE'
