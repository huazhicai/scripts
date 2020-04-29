#coding:utf-8

import init

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from dlg import SaveQuestionDialog

def doneChoose(self, choice):
	print choice

def test():
	from PyQt5.QtGui import QApplication
	import sys 
	app = QApplication(sys.argv)
	w = SaveQuestionDialog(doneChoice=doneChoose)
	w.show()
	app.exec_()

if __name__ == '__main__':
	test()

