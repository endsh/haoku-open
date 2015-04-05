# coding: utf-8
import conf
from .base import *

STATUS = conf.STATUS
if STATUS == 'RELEASE':
	from .release import *
elif STATUS == 'TEST':
	from .test import *