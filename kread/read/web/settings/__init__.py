# coding: utf-8
import conf
from .base import *

if conf.TEST:
	from .test import *
elif conf.RELEASE:
	from .release import *