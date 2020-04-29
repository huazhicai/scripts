from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal, QPointF, QPoint
from PyQt5.QtWidgets import QGraphicsView


class DiagramView(QGraphicsView):
    mouseMoved = pyqtSignal(int, int)

    def __init__(self, scene):
        super(DiagramView, self).__init__(scene)
        self.setAcceptDrops(True)
        self.setCacheMode(QGraphicsView.CacheBackground)

        self.cumulativeScale = 1.0

        # 开始移动画布时，鼠标点击的画布的位置
        # self.gMoveStart = None
        self.moveStart = None
        # 开始移动画布时，可见区域中心对应的场景中心坐标
        self.gCenter = None
        self.moveFlag = False

        # 关闭垂直和水平方向的滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Qt::ScrollBarAlwaysOff

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.moveFlag = True

        super(DiagramView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.moveFlag and self.moveStart is None:
            self.moveStart = event.pos()
            self.gCenter = self.mapToScene(self.size().width() / 2,
                                           self.size().height() / 2)
            self.viewport().setCursor(Qt.ClosedHandCursor)

        if self.moveStart:
            moveStart2 = event.pos()
            gMoveStart = self.mapToScene(self.moveStart)
            gMoveStart2 = gMoveStart + 1.0 / self.cumulativeScale * (moveStart2 - self.moveStart)
            gCenter2 = gMoveStart2 - gMoveStart + self.gCenter
            oo2 = gCenter2 - self.gCenter
            newo = self.gCenter - oo2
            self.centerOn(newo)

        cPoint = self.mapToScene(event.pos())
        self.mouseMoved.emit(cPoint.x(), cPoint.y())

        super(DiagramView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.moveFlag:
            self.moveStart = None
            self.gCenter = None
            self.viewport().setCursor(Qt.ArrowCursor)
            self.moveFlag = False
        super(DiagramView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor

            # Save the scene pos
            oldPos = self.mapToScene(event.pos())

            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor

            # 最小不要缩小到原比例的1/10以下
            if self.cumulativeScale < 0.1 and zoomFactor < 1:
                return

            self.scale(zoomFactor, zoomFactor)
            self.cumulativeScale *= zoomFactor

            # Get the new position
            newPos = self.mapToScene(event.pos())

            # Move scene to old position
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())
            return

        # 注释此行来开关对滚动条的支持
        super(DiagramView, self).wheelEvent(event)

    def dragEnterEvent(self, event):
        pass

    def pointToPointF(self, point):
        return QPointF(point.x(), point.y())

    def pointFToPoint(self, pointF):
        x = int(pointF.x())
        y = int(pointF.y())

        return QPoint(x, y)
