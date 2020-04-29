# coding:utf-8
from PyQt5.QtCore import *
import sys

from PyQt5.QtWidgets import *


class CommentWindow(QMainWindow):
    """
    can't set a QLayout directly on the QMainWindow.
    You need to create a QWidget and set it as the central widget on the QMainWindow
    and assign the QLayout to that. It just doesn't accept layouts
    """
    def __init__(self, parent=None):
        super(CommentWindow, self).__init__(parent)
        # 子控件，不用传递父控件，因为有布局管理器做为中间连接
        item = QGraphicsTextItem('Data')
        # 设置文本交互标志，文本可编辑
        item.setTextInteractionFlags(Qt.TextEditable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)
        item.setFlag(QGraphicsItem.ItemIsMovable)

        # 创建图形场景对象
        scene = QGraphicsScene()
        scene.addItem(item)

        # 创建图形视口对象，传递图形场景
        view = QGraphicsView(scene)
        # 1. 创建布局管理器对象
        layout = QVBoxLayout()
        layout.addWidget(view)
        # 2. 直接把布局管理器对象设置给需要布局的父控件
        # self.setLayout(layout)

        # 主控件
        self.main_widget = QWidget()
        # 把布局管理器对象设置给需要布局的父控件
        self.main_widget.setLayout(layout)
        self.setCentralWidget(self.main_widget)


if __name__ == '__main__':
    # 1.创建一个应用程序，传递命令行参数列表
    app = QApplication(sys.argv)
    # 2。创建控件
    w = CommentWindow()
    # 2.1 设置控件
    w.setGeometry(0, 0, 300, 400)
    # 2.2 展示控件
    w.show()
    # 3. 应用程序执行，进入到消息循环
    sys.exit(app.exec_())
