#coding:utf-8
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys 

class Rect(QGraphicsItem):
	def __init__(self,parent=None, scene=None):
		super(Rect, self).__init__(parent,scene)

		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)

	def mousePressEvent(self, event):
		if event.button() != Qt.LeftButton:
			event.ignore()
			return

	def boundingRect(self):
		return QRectF(-100,-50,200,100)

	def paint(self,painter, option, widget=None):
		painter.drawRect(-100,-50,200,100)

class MyScene(QGraphicsScene):
	def __init__(self,parent=None):
		super(MyScene, self).__init__(parent)

		self.menu = QMenu()
		actionA = self.menu.addAction(u'Action A')
		actionB = self.menu.addAction(u'Action B')
		actionC = self.menu.addAction(u'Action C')

		self.submenu = self.menu.addMenu(u'Components')
		subA = self.submenu.addAction(u'Sub A')
		subB = self.submenu.addAction(u'Sub B')
		subC = self.submenu.addAction(u'Sub C')

		actionA.triggered.connect(self.aClicked)
		actionB.triggered.connect(self.bClicked)
		actionC.triggered.connect(self.cClicked)

		subA.triggered.connect(self.subAClicked)
		subB.triggered.connect(self.subBClicked)
		subC.triggered.connect(self.subCClicked)

	def contextMenuEvent(self,event):
		self.menu.exec_(event.screenPos())

	def aClicked(self):
		print 'in a'

	def bClicked(self):
		print 'in b'

	def cClicked(self):
		print 'in c'

	def subAClicked(self):
		print 'sub A'

	def subBClicked(self):
		print 'sub B'

	def subCClicked(self):
		print 'sub C'

class MyView(QGraphicsView):
	def __init__(self,scene, parent=None):
		super(MyView, self).__init__(scene, parent)

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		scene = MyScene()
		rect = Rect()
		scene.addItem(rect)
		rect.setPos(0,0)

		view = QGraphicsView(scene)

		self.setCentralWidget(view)

def main():
	app = QApplication(sys.argv)
	w = MainWindow()
	w.show()
	app.exec_()

if __name__ == '__main__':
	main()

