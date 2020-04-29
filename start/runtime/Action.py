#-*- coding: utf-8 -*-
"""
copyright. AIIT
created by liqing. 
contact blacknepia@dingtail.com for more information
"""


class Action(object):

	def __call__(self, args, io):
		raise NotImplementedError

