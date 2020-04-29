#coding:utf-8

import init
from util import interpolate_cosine_points
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial
import sys

class PaintDialog(QDialog):
	def __init__(self,parent=None):
		super(PaintDialog, self).__init__(parent)

	def paintEvent(self,event):
		painter = QPainter(self)
		path = QPainterPath()
		path.moveTo(200,50)
		path.arcTo(150,0,50,50,0,90)
		path.arcTo(50,0,50,50,90,90)
		path.arcTo(50,50,50,50,180,90)
		path.arcTo(150,50,50,50,270,90)
		path.lineTo(200, 50)

		linepen = QPen()
		linepen.setWidth(2)
		linepen.setColor(Qt.red)

		painter.setPen(linepen)
		painter.drawPath(path)

class TestDialog(QDialog):
	def __init__(self):
		super(TestDialog,self).__init__()

		toolBox = QToolBox(self)
		addButton = QPushButton('add')
		deleteButton = QPushButton('delete')

		label = QLabel('Hello')
		layout = QVBoxLayout()
		layout.addWidget(addButton)
		layout.addWidget(deleteButton)

		widget = QWidget()
		widget.setLayout(layout)
		buttonStrange = QPushButton('lisi')

		toolBox.addItem(widget,'Friend')
		toolBox.addItem(buttonStrange, 'Strange')

		toolBox.layout().setSpacing(0)

		hLayout = QHBoxLayout()
		hLayout.addWidget(toolBox)
		hLayout.setMargin(0)

		self.setLayout(hLayout)
		self.resize(100,200)
		self.setWindowTitle('QToolBoxDemo')

class CosineDialog(QDialog):
	def __init__(self,parent=None):
		super(CosineDialog, self).__init__()

	def paintEvent(self,event):
		painter = QPainter(self)

		path = QPainterPath()
		# case 1: (500,180) -> (100,100)
		# case 2: (100,100) -> (500,180)
		# case 3: (100,500) -> (400,100)
		# case 4: (400,100) -> (100,500)
		# case 5: (100,100) -> (400,100)
		# case 6: (100,100) -> (100,500)
		path.moveTo(400,100)
		for p in interpolate_points(400,100,100,500):
			path.lineTo(p[0],p[1])

		linepen = QPen()
		linepen.setWidth(1)
		linepen.setColor(Qt.red)
		linepen.setCapStyle(Qt.FlatCap)

		painter.setPen(linepen)
		painter.drawPath(path)

class EllepiseDialog(QDialog):
	def __init__(self,parent=None):
		super(EllepiseDialog, self).__init__()

	def paintEvent(self,event):
		painter = QPainter(self)

		linepen = QPen()
		linepen.setWidth(1)
		linepen.setColor(Qt.red)
		painter.setPen(linepen)

		painter.drawEllipse(100,100,50,30)
		painter.drawEllipse(100,100,5,5)

class MyRectItem(QGraphicsItem):
	def __init__(self,parent=None, scene=None):
		super(MyRectItem, self).__init__(parent,scene)

		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)

	def mousePressEvent(self, event):
		if event.button() != Qt.LeftButton:
			event.ignore()
			return

		print 'in Parent'

	def boundingRect(self):
		return QRectF(-100,-50,200,100)

	def paint(self,painter, option, widget=None):
		painter.drawRect(-100,-50,200,100)

class MySubItem(QGraphicsItem):
	def __init__(self,parent=None, scene=None):
		super(MySubItem, self).__init__(parent,scene)

		self.setFlag(QGraphicsItem.ItemIsSelectable, True)

	def mousePressEvent(self, event):
		if event.button() != Qt.LeftButton:
			event.ignore()
			return

		print 'in Sub'
		super(MySubItem,self).mousePressEvent(event)

	def mouseDoubleClickEvent(self,event):
		print 'in double click'
		super(MySubItem,self).mouseDoubleClickEvent(event)

	def boundingRect(self):
		return QRectF(-10,-10,20,20)

	def paint(self, painter, option, widget=None):
		painter.drawRect(-10,-10,20,20)

class RightMainWindow(QMainWindow):
	def __init__(self):
		super(RightMainWindow, self).__init__()
		self.createContextMenu()
		self.setWindowTitle('Hello')

	def createContextMenu(self):
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.showContextMenu)

		self.contextMenu = QMenu(self)
		if self.contextMenu is None:
			print 'contextMenu is None'
		self.actionA = self.contextMenu.addAction(u'Action A')
		self.actionB = self.contextMenu.addAction(u'Action B')
		self.actionC = self.contextMenu.addAction(u'Action C')

		self.actionA.triggered.connect(partial(self.actionHandler,u'Action A'))
		self.actionB.triggered.connect(partial(self.actionHandler,u'Action B'))
		self.actionC.triggered.connect(partial(self.actionHandler,u'Action C'))

	def showContextMenu(self, pos):
		self.contextMenu.move(self.pos() + pos)
		self.contextMenu.show()

	def actionHandler(self,text):
		print 'action handler',text

class DoubleClickWindow(QMainWindow):
	def __init__(self):
		super(DoubleClickWindow, self).__init__()

		item = MyRectItem()
		subitem = MySubItem(parent=item)
		subitem.setPos(-10,-10)

		scene = QGraphicsScene()
		scene.addItem(item)

		view = QGraphicsView(scene)
		layout = QVBoxLayout()
		layout.addWidget(view)

		self.main_widget = QWidget()
		self.main_widget.setLayout(layout)

		self.setCentralWidget(self.main_widget)

def subitem_demo():
	w = DoubleClickWindow()
	w.show()

def rightmenu_demo():
	w = RightMainWindow()
	w.show()

def main():
	app = QApplication(sys.argv)
	w = DoubleClickWindow()
	w.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
