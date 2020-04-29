# coding:utf-8

from PyQt5.QtCore import QPointF
import numpy as np


def pyqtPoint():
    moveStart = QPointF(-20, 908)
    moveStart2 = QPointF(100, 200)
    gCenter = QPointF(500, 200)
    cumulativeScale = 0.73
    gMoveStart = QPointF(0, 203)

    gMoveStart2 = gMoveStart + 1.0 / cumulativeScale * (moveStart2 - moveStart)
    gCenter2 = gMoveStart2 - gMoveStart + gCenter
    oo2 = gCenter2 - gCenter
    newo = gCenter - oo2

    return newo
