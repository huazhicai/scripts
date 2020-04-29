# coding:utf-8
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QVBoxLayout


class AttrPanel(QWidget):
    valueUpdated = pyqtSignal(str)

    def __init__(self):
        super(AttrPanel, self).__init__()

        nameLabel = QLabel('Name')
        self.nameInput = QLineEdit('')

        changeButton = QPushButton('change')
        changeButton.clicked.connect(self.changeClicked)
        wlayout = QGridLayout()
        wlayout.addWidget(nameLabel, 0, 0)
        wlayout.addWidget(self.nameInput, 0, 1)
        wlayout.addWidget(changeButton, 1, 1)
        widget = QWidget()
        widget.setLayout(wlayout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(widget)

        self.setLayout(main_layout)

        self.setMinimumWidth(200)

    def setModel(self, model):
        self.model = model

    def changeClicked(self):
        # print 'value changed to %s' % self.nameInput.text()
        self.valueUpdated.emit(self.nameInput.text())
