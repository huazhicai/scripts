# coding:utf-8

import init

from dlg import SaveQuestionDialog


def doneChoose(self, choice):
    print(choice)


def test():
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    w = SaveQuestionDialog(doneChoice=doneChoose)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
