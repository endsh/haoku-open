# coding: utf-8
import conf
from .base import *


if conf.RELEASE:
	from .release import *