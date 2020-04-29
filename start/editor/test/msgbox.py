# coding:utf-8


import sys

from PyQt5.QtWidgets import QApplication, QMessageBox


def test():
    app = QApplication(sys.argv)
    # 没有父控件，当做顶层控件
    QMessageBox.warning(None,
                        'Warning',
                        'query类型的节点不能有输入，请修改',
                        QMessageBox.Ok)
    app.exec_()


if __name__ == '__main__':
    test()
