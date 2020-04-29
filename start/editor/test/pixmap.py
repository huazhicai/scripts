# coding:utf-8
import sys

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *


class MyRectItem(QGraphicsItem):
    def __init__(self, parent=None):
        super(MyRectItem, self).__init__(parent)

        # 矩形框对象可移动
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        # 矩形框对象可选择
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        """鼠标按压事件，如果不是左击，忽略事件"""
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        print('in Parent')

    def boundingRect(self):
        """绘画的矩形限制边界，视图中心为坐标原点，鼠标能够点击区域"""
        return QRectF(-100, -50, 200, 100)

    def paint(self, painter, option, widget=None):
        """绘画，画了一个矩形，坐标(-100, -50), 长宽200*100"""
        painter.drawRect(-100, -50, 200, 100)


class MySubItem(QGraphicsItem):
    def __init__(self, parent=None):
        super(MySubItem, self).__init__(parent)

        # 矩形坐标和尺寸
        self.rect = QRectF(-10, -10, 20, 20)
        # png像素图，没有图层，不能对图片进行修改
        self.pixmap = QPixmap('../images/pen.png')

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
        """绘画限制边界"""
        return self.rect

    def paint(self, painter, option, widget=None):
        """绘画矩形框，绘制像素图片"""
        painter.drawRect(self.rect)
        source = QRectF(0, 0, 20, 20)
        painter.drawPixmap(self.rect, self.pixmap, source)


class DoubleClickWindow(QMainWindow):
    def __init__(self, parent=None):
        super(DoubleClickWindow, self).__init__(parent)

        # 创建图形项目控件对象
        item = MyRectItem()
        subitem = MySubItem(parent=item)
        # 设置子对象坐标位置
        subitem.setPos(-10, -10)

        # 创建图形场景对象
        scene = QGraphicsScene()
        # 图像场景中添加item
        scene.addItem(item)

        # 创建图形视口对象，传递图形场景作为参数
        view = QGraphicsView(scene)
        # 创建垂直布局管理器对象
        layout = QVBoxLayout()
        # 添加子控件图形视口对象到布局器中
        layout.addWidget(view)

        # 创建父类控件
        self.main_widget = QWidget()
        # 把布局管理器对象设置给需要布局的父对象
        self.main_widget.setLayout(layout)

        # 窗口对象拔父控件设置为中央控件
        self.setCentralWidget(self.main_widget)


def test():
    app = QApplication(sys.argv)
    w = DoubleClickWindow()
    w.setWindowTitle("DoubleClickWindow")
    w.setGeometry(200, 200, 500, 500)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
