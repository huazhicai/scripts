# coding:utf-8
import sys
from PyQt5.QtCore import QRectF

from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # 创建图形场景， 有布局不用传入self
        scene = QGraphicsScene()
        # 设置场景边框， 浮点精度矩形
        scene.setSceneRect(QRectF(-2000, -2000, 4000, 4000))
        # 创建矩形框项目对象
        rect = QGraphicsRectItem(QRectF(-50, -50, 100, 100))
        # 矩形框对象添加到图形场景中
        scene.addItem(rect)
        # 设置图形框在场景中的坐标位置
        rect.setPos(0, 0)

        # 创建图形视口，传递图形场景参数
        view = QGraphicsView(scene)

        # 创建标签控件对象
        label = QLabel()
        label.setText('<h1>Hello</h1>')

        # 1. 创建一个网格布局管理器对象， 传递基类控件对象
        layout = QGridLayout()
        # 添加图形视口对象控件，并坐标
        layout.addWidget(view, 0, 0, 100, 5)
        # 添加标签控件
        layout.addWidget(label, 0, 0, 1, 300)

        # 创建基类控件对象
        mainWidget = QWidget()
        # 把布局管理器对象设置给需要布局的父类控件
        mainWidget.setLayout(layout)
        # 在窗口控件对象中，把mainWidget对象设置为中心控件
        self.setCentralWidget(mainWidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建顶层控件
    w = MainWindow()
    w.setGeometry(100, 100, 500, 500)
    w.show()
    # 3. 应用程序的执行, 进入到消息循环
    sys.exit(app.exec_())
