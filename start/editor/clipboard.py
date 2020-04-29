# coding:utf-8

from util import singleton
from copy import deepcopy


@singleton
class GraphisClipboard(object):
	def __init__(self):
		# self.item = None 
		self.itemList = []

	def clear(self):
		# self.item = None 
		self.itemList = []

	def clearItems(self):
		self.itemList = []

	def setGraphicsItems(self, items):
		if self.hasGraphicsItems(): self.clearItems()
		for item in items:
			self.itemList.append(item)

	def hasGraphicsItems(self):
		return len(self.itemList) != 0

	def graphicsItems(self):
		return deepcopy(self.itemList)

	def clearItem(self):
		self.item = None

	def setGraphicsItem(self, item):
		if self.hasGraphicsItem(): self.clearItem()
		self.item = item

	def hasGraphicsItem(self):
		return self.item is not None

	def graphicsItem(self):
		return deepcopy(self.item)
