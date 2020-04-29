# coding:utf-8
import sys

from util import interpolate_cosine_points
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial


class PaintDialog(QDialog):
    def __init__(self, parent=None):
        super(PaintDialog, self).__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)  # 1.画师对象
        path = QPainterPath()  # 2.子空件绘画路径对象
        # 移动画笔起始点，默认是在（0，0）开始画的
        path.moveTo(200, 50)
        path.arcTo(150, 0, 50, 50, 0, 90)
        path.arcTo(50, 0, 50, 50, 90, 90)
        path.arcTo(50, 50, 50, 50, 180, 90)
        path.arcTo(150, 50, 50, 50, 270, 90)
        path.lineTo(200, 50)

        linepen = QPen()  # 3.子空件画笔对象
        # 画笔属性设置
        linepen.setWidth(2)
        linepen.setColor(Qt.red)

        # 4.把画笔对象设置给绘画师对象
        painter.setPen(linepen)
        # 5. 绘画师调用绘画技能，按照绘画路径绘画
        painter.drawPath(path)


class TestDialog(QDialog):
    def __init__(self):
        super(TestDialog, self).__init__()

        # 子控件，传递父控件TestDialog对象
        toolBox = QToolBox(self)
        # 子控件
        addButton = QPushButton('add')
        deleteButton = QPushButton('delete')
        label = QLabel('Hello')

        # 子空件中的布局对象
        layout = QVBoxLayout()
        layout.addWidget(addButton)
        layout.addWidget(deleteButton)
        layout.addWidget(label)

        # 主控件，用来接收布局对象
        widget = QWidget()
        # 把布局管理器对象设置给需要布局的主控件对象
        widget.setLayout(layout)

        # 孙控件
        buttonStrange = QPushButton('lisi')
        toolBox.addItem(widget, 'Friend')
        toolBox.addItem(buttonStrange, 'Strange')

        # 设置子空件间距
        toolBox.layout().setSpacing(0)

        # 水平布局管理器对象
        hLayout = QHBoxLayout()
        hLayout.addWidget(toolBox)
        hLayout.setContentsMargins(0, 0, 0, 0)

        # 把布局管理器对象设置给需要布局的父对象控件
        self.setLayout(hLayout)
        # 调整用户界面尺寸
        self.resize(100, 200)
        self.setWindowTitle('QToolBoxDemo')


class CosineDialog(QDialog):
    def __init__(self, parent=None):
        super(CosineDialog, self).__init__()

    def paintEvent(self, event):
        # 1.画师对象
        painter = QPainter(self)
        # 2.画图路径对象
        path = QPainterPath()
        # case 1: (500,180) -> (100,100)
        # case 2: (100,100) -> (500,180)
        # case 3: (100,500) -> (400,100)
        # case 4: (400,100) -> (100,500)
        # case 5: (100,100) -> (400,100)
        # case 6: (100,100) -> (100,500)
        # 属性设置，
        path.moveTo(400, 100)  # 移动画笔初始点
        for p in interpolate_cosine_points(400, 100, 100, 500):
            path.lineTo(p[0], p[1])

        # 3.画笔对象
        linepen = QPen()
        # 画笔属性设置
        linepen.setWidth(1)
        linepen.setColor(Qt.red)
        linepen.setCapStyle(Qt.FlatCap)

        # 4.画师执画笔
        painter.setPen(linepen)
        # 5.画师按路径画图
        painter.drawPath(path)


class EllepiseDialog(QDialog):
    def __init__(self, parent=None):
        super(EllepiseDialog, self).__init__()

    def paintEvent(self, event):
        painter = QPainter(self)  # 1.创建子空件画师对象，传递父空件对象做参数

        linepen = QPen()  # 2.创建子空件画笔对象
        # 画笔对象属性设置
        linepen.setWidth(1)
        linepen.setColor(Qt.red)
        # 3.画笔对象设置给画师
        painter.setPen(linepen)

        # 在坐标点为Point(100, 100), 长*宽=50*30的矩形内画内接椭圆
        painter.drawEllipse(0, 0, 50, 50)
        painter.drawEllipse(100, 100, 5, 5)


class MyRectItem(QGraphicsRectItem):
    def __init__(self, parent=None):
        super(MyRectItem, self).__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        print('in Parent')

    def boundingRect(self):
        """外边框"""
        return QRectF(-100, -50, 200, 100)

    def paint(self, painter, option, widget=None):
        painter.drawRect(-100, -50, 200, 100)


class MySubItem(QGraphicsItem):
    def __init__(self, parent=None):
        super(MySubItem, self).__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            return

        print('in Sub')
        super(MySubItem, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        print('in double click')
        super(MySubItem, self).mouseDoubleClickEvent(event)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter, option, widget=None):
        painter.drawRect(-10, -10, 20, 20)


class RightMainWindow(QMainWindow):
    def __init__(self):
        super(RightMainWindow, self).__init__()
        self.createContextMenu()
        self.setWindowTitle('Hello')

    def createContextMenu(self):
        # 自定义右键菜单栏
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 信号槽函数
        self.customContextMenuRequested.connect(self.showContextMenu)

        # 上下文菜单控件对象
        self.contextMenu = QMenu(self)
        if self.contextMenu is None:
            print('contextMenu is None')
        self.actionA = self.contextMenu.addAction('Action A')
        self.actionB = self.contextMenu.addAction('Action B')
        self.actionC = self.contextMenu.addAction('Action C')

        # 触发槽
        self.actionA.triggered.connect(partial(self.actionHandler, 'Action A'))
        self.actionB.triggered.connect(partial(self.actionHandler, 'Action B'))
        self.actionC.triggered.connect(partial(self.actionHandler, 'Action C'))

    def showContextMenu(self, pos):
        self.contextMenu.move(self.pos() + pos)
        self.contextMenu.show()

    def actionHandler(self, text):
        print('action handler', text)


class DoubleClickWindow(QMainWindow):
    def __init__(self):
        super(DoubleClickWindow, self).__init__()

        # 主控件对象
        item = MyRectItem()
        # 子控件
        subitem = MySubItem(parent=item)
        # 设置在场景中的坐标位置
        subitem.setPos(-10, -10)

        # 创建图形场景对象
        scene = QGraphicsScene()
        # 主控件加入对象中
        scene.addItem(item)

        # 创建图形视口对象，传递场景对象做为参数
        view = QGraphicsView(scene)
        # 创建垂直布局对象
        layout = QVBoxLayout()
        # 子控件加入布局对象中
        layout.addWidget(view)

        # 创建父类控件，用以布局
        self.main_widget = QWidget()
        # 把布局管理器对象设置给需要布局的父对象
        self.main_widget.setLayout(layout)

        # 把父控件对象设置为窗口中央位置
        self.setCentralWidget(self.main_widget)


def main():
    app = QApplication(sys.argv)
    # w = DoubleClickWindow()
    # w = TestDialog()
    # w = RightMainWindow()
    # w = EllepiseDialog()
    # w = PaintDialog()
    w = CosineDialog()
    w.show()
    w.setGeometry(20, 20, 500, 500)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
