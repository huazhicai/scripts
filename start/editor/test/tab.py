# coding:utf-8
import sys

from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Tab窗口')

        # 窗口tab控件，祖父控件
        self.tabWidget = QTabWidget()
        # preferred 推荐大小为优先选择，可以变大或者变小
        # ignore 不能感知到推荐的大小，会以尽可能大的空间来放置窗口部件
        # 如同浏览器的open link in new table， table 大小会变化
        self.tabWidget.setSizePolicy(QSizePolicy.Preferred,
                                     QSizePolicy.Ignored)
        self.tabWidget.setMovable(True)  # 可移动

        # 抽象类控件，主控件，用来接收布局
        tab1 = QWidget()
        # 表格控件10行10列
        tableWidget = QTableWidget(10, 10)
        # 布局对象
        tab1Hbox = QHBoxLayout()
        tab1Hbox.setContentsMargins(15, 15, 15, 15)
        tab1Hbox.addWidget(tableWidget)
        tab1.setLayout(tab1Hbox)

        # 抽象类控件，主控件，用来接收布局
        tab2 = QWidget()
        # 文本编辑控件，因为有布局，所以传入父类控件
        textEdit = QTextEdit()
        # 写入文本
        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n"
                              "Up above the world so high,\n"
                              "Like a diamond in the sky.\n"
                              "Twinkle, twinkle, little star,\n"
                              "How I wonder what you are!\n")
        tab2hbox = QHBoxLayout()
        # 设置边距
        tab2hbox.setContentsMargins(150, 25, 35, 55)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)

        # 父类控件加入祖父类控件
        self.tabWidget.addTab(tab1, 'Table')
        self.tabWidget.addTab(tab2, 'Text Edit')
        # 居中
        self.setCentralWidget(self.tabWidget)


def test():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.setGeometry(10, 10, 300, 300)
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
