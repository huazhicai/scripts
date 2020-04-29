#coding:utf-8
try:
	from PySide.QtGui import QUndoCommand
	from PySide.QtCore import QPointF
except:
	from PyQt5.QtGui import QUndoCommand
	from PyQt5.QtCore import QPointF

class CommandAdd(QUndoCommand):
	def __init__(self,controller,scene,item,pos,description=''):
		super(CommandAdd,self).__init__(description)
		self.controller = controller
		self.scene = scene
		self.item = item 
		self.pos = pos

	def redo(self):
		self.controller.addNode(self.item)
		self.scene.addItem(self.item)
		self.item.setPos(self.pos)
		self.scene.addToCache(self.item)

	def undo(self):
		self.controller.removeNode(self.item)
		self.scene.removeItem(self.item)
		self.scene.removeFromCache(self.item)

class CommandDelete(QUndoCommand):
	def __init__(self,controller,item,description=''):
		super(CommandDelete,self).__init__(description)

		self.controller = controller
		self.scene = item.scene()
		self.item = item 
		self.comment = self.item.comment
		self.pos = item.scenePos()
		self.arrows = {}
		childItems = self.item.childItems()
		for cItem in childItems:
			self.arrows[cItem] = cItem.arrows[:]

	def redo(self):
		# 先移除关联的边数据
		for cItem in self.arrows.keys():
			childItemArrows = self.arrows[cItem]
			for arrow in childItemArrows:
				self.controller.removeEdge(
					arrow.startItem().parentItem(),
					arrow.endItem().parentItem(),
					arrow.startItem().itemType.typeId,
					arrow.endItem().itemType.typeId)

		# 再删除定点数据
		self.controller.removeNode(self.item)

		# 移除子item中的边
		childItems = self.item.childItems()
		for cItem in childItems:
			cItem.removeArrows()
		# 移除item中的边
		self.item.removeArrows()

		# 如果有注释的化，先删除注释
		if self.comment is not None:
			self.scene.removeItem(self.comment)
		
		# 移除item
		self.scene.removeItem(self.item)
		self.scene.removeFromCache(self.item)

	def undo(self):
		self.scene.addItem(self.item)
		self.scene.addToCache(self.item)
		
		self.item.setPos(self.pos)
		# 如果有comment，要添加comment
		if self.comment is not None:
			self.scene.addItem(self.comment)
			topLeft = self.item.polygon()[0] + self.pos
			commentPos = topLeft + QPointF(0,-50)
			self.comment.setPos(commentPos)
		self.controller.addNode(self.item)

		for cItem in self.arrows.keys():
			childItemArrows = self.arrows[cItem]
			for arrow in childItemArrows:
				self.scene.addItem(arrow)
				startItem = arrow.startItem()
				endItem = arrow.endItem()
				startItem.addArrow(arrow)
				endItem.addArrow(arrow)
				self.controller.addEdge(
					startItem.parentItem(),
					endItem.parentItem(),
					startItem.itemType, 
					endItem.itemType, 
					startItem.itemContent.contentType)

class CommandLink(QUndoCommand):
	def __init__(self,controller,scene,arrow,description=''):
		super(CommandLink,self).__init__(description)
		self.arrow = arrow 
		self.scene = scene 
		self.controller = controller

	def redo(self):
		self.controller.addEdge(self.arrow.startItem().parentItem(),
			self.arrow.endItem().parentItem(),
			self.arrow.startItem().itemType,
			self.arrow.endItem().itemType,
			self.arrow.startItem().itemContent.contentType)

		self.arrow.startItem().addArrow(self.arrow)
		self.arrow.endItem().addArrow(self.arrow)
		self.arrow.setZValue(-1000.0)
		self.scene.addItem(self.arrow)
		self.arrow.updatePosition()
		# 连线后不再具有值
		self.arrow.endItem().itemContent.contentValue = None
		self.arrow.startItem().update()
		self.arrow.endItem().update()

	def undo(self):
		self.controller.removeEdge(self.arrow.startItem().parentItem(),
			self.arrow.endItem().parentItem(),
			self.arrow.startItem().itemType.typeId, 
			self.arrow.endItem().itemType.typeId)

		self.arrow.startItem().removeArrow(self.arrow)
		self.arrow.endItem().removeArrow(self.arrow)
		# 恢复默认值
		self.arrow.endItem().itemContent.contentValue = self.arrow.endItem().itemContent.defaultValue
		self.arrow.startItem().update()
		self.arrow.endItem().update()
		self.scene.removeItem(self.arrow)

class CommandUnLink(QUndoCommand):
	def __init__(self,controller, arrow, description=''):
		super(CommandUnLink, self).__init__(description)
		self.controller = controller 
		self.arrow = arrow
		self.scene = arrow.scene()

	def redo(self):
		self.controller.removeEdge(self.arrow.startItem().parentItem(),
			self.arrow.endItem().parentItem(),
			self.arrow.startItem().itemType.typeId,
			self.arrow.endItem().itemType.typeId)

		self.arrow.startItem().removeArrow(self.arrow)
		self.arrow.endItem().removeArrow(self.arrow)
		# 恢复默认值
		self.arrow.endItem().itemContent.contentValue = self.arrow.endItem().itemContent.defaultValue
		self.arrow.startItem().update()
		self.arrow.endItem().update()
		self.scene.removeItem(self.arrow)

	def undo(self):
		self.controller.addEdge(self.arrow.startItem().parentItem(),
			self.arrow.endItem().parentItem(),
			self.arrow.startItem().itemType,
			self.arrow.endItem().itemType,
			self.arrow.startItem().itemContent.contentType)

		self.arrow.startItem().addArrow(self.arrow)
		self.arrow.endItem().addArrow(self.arrow)
		self.arrow.setZValue(-1000.0)
		self.scene.addItem(self.arrow)
		self.arrow.updatePosition()
		# 不能具有值
		self.arrow.endItem().itemContent.contentValue = None
		self.arrow.startItem().update()
		self.arrow.endItem().update()
