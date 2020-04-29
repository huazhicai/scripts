#coding:utf-8
import init
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

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
		self.rect = QRectF(-10,-10,20,20)
		self.pixmap = QPixmap('../images/pen.png')

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
		return self.rect

	def paint(self, painter, option, widget=None):
		painter.drawRect(self.rect)
		source = QRectF(0,0,20,20)
		painter.drawPixmap(self.rect,self.pixmap,source)

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

def test():
	app = QApplication(sys.argv)
	w = DoubleClickWindow()
	w.show()
	app.exec_()

if __name__ == '__main__':
	test()

