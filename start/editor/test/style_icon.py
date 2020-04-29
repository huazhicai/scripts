from PyQt5.QtWidgets import QGridLayout, QPushButton, QStyle

layout = QGridLayout()
iconIndex = 0

for row in range(7):
    for col in range(10):
        standardIcon = iconIndex
        layout.addWidget(QPushButton(QStyle.standardIcon(standardIcon)))