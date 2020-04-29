# coding:utf-8
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from functools import partial
# import animatedtiles_rc2
from PyQt5.QtWidgets import *


class Button(QGraphicsWidget):
    pressed = pyqtSignal()

    def __init__(self, pixmap, parent=None):
        super(Button, self).__init__(parent)

        self._pix = pixmap
        self.setAcceptHoverEvents(True)  # 设置接收鼠标悬浮事件
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-65, -65, 130, 130)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, option, widget=None):
        down = option.state & QStyle.State_Sunken
        r = self.boundingRect()

        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        if option.state & QStyle.State_MouseOver:
            color_0 = Qt.white
        else:
            color_0 = Qt.lightGray

        color_1 = Qt.darkGray

        if down:
            color_0, color_1 = color_1, color_0

        grad.setColorAt(0, color_0)
        grad.setColorAt(1, color_1)

        painter.setPen(Qt.darkGray)
        painter.setBrush(grad)
        painter.drawEllipse(r)

        color_0 = Qt.darkGray
        color_1 = Qt.lightGray

        if down:
            color_0, color_1 = color_1, color_0

        grad.setColorAt(0, color_0)
        grad.setColorAt(1, color_1)

        painter.setPen(Qt.NoPen)
        painter.setBrush(grad)

        if down:
            painter.translate(2, 2)

        painter.drawEllipse(r.adjusted(5, 5, -5, -5))
        painter.drawPixmap(-self._pix.width() / 2, -self._pix.height() / 2,
                           self._pix)

    def mousePressEvent(self, event):
        self.pressed.emit()
        self.update()

    def mouseReleaseEvent(self, event):
        self.update()


# class ButtonPanel(QGraphicsRectItem):
#	def __init__(self):
#		super(ButtonPanel, self).__init__()
#		ellipseButton = Button(QPixmap(':/images/ellipse.png'), self)
#		figure8Button = Button(QPixmap(':/images/figure8.png'), self)
#		randomButton = Button(QPixmap(':/images/random.png'), self)
#		tiledButton = Button(QPixmap(':/images/tile.png'), self)
#		centeredButton = Button(QPixmap(':/images/centered.png'), self)

#		ellipseButton.setPos(-100, -100)
#		figure8Button.setPos(100, -100)
#		randomButton.setPos(0, 0)
#		tiledButton.setPos(-100, 100)
#		centeredButton.setPos(100, 100)

#		ellipseButton.pressed.connect(partial(self.notice,'ellipse'))
#		figure8Button.pressed.connect(partial(self.notice,'figure'))
#		randomButton.pressed.connect(partial(self.notice,'random'))
#		tiledButton.pressed.connect(partial(self.notice,'tiled'))
#		centeredButton.pressed.connect(partial(self.notice,'centered'))

#	def notice(self,name):
#		print 'in notice',name
#		if name == 'random':
#			self.scene().animation.start()

class ButtonPanel(QObject):
    def __init__(self):
        super(ButtonPanel, self).__init__()

        self.panel = QGraphicsRectItem()
        ellipseButton = Button(QPixmap(':/images/ellipse.png'), self.panel)
        figure8Button = Button(QPixmap(':/images/figure8.png'), self.panel)
        randomButton = Button(QPixmap(':/images/random.png'), self.panel)
        tiledButton = Button(QPixmap(':/images/tile.png'), self.panel)
        centeredButton = Button(QPixmap(':/images/centered.png'), self.panel)

        ellipseButton.setPos(-100, -100)
        figure8Button.setPos(100, -100)
        randomButton.setPos(0, 0)
        tiledButton.setPos(-100, 100)
        centeredButton.setPos(100, 100)

        ellipseButton.pressed.connect(partial(self.notice, 'ellipse'))
        figure8Button.pressed.connect(partial(self.notice, 'figure'))
        randomButton.pressed.connect(partial(self.notice, 'random'))
        tiledButton.pressed.connect(partial(self.notice, 'tiled'))
        centeredButton.pressed.connect(partial(self.notice, 'centered'))

        self.buttons = [ellipseButton, figure8Button, tiledButton, centeredButton]

    def _set_pos(self, pos):
        self.panel.setPos(pos)

    def _set_rect(self, rect):
        self.panel.setRect(rect)

    def _set_fold(self, fold):
        print(('in set_fold', fold))
        for btn in self.buttons:
            btn.setGeometry(fold)

    pos = pyqtProperty(QPointF, fset=_set_pos)
    rect = pyqtProperty(QRectF, fset=_set_rect)
    fold = pyqtProperty(QRectF, fset=_set_fold)

    def notice(self, name):
        print(('in notice', name))
        if name == 'random':
            self.panel.scene().animation.start()


class MyScene(QGraphicsScene):
    """场景控件"""

    def __init__(self):
        super(MyScene, self).__init__()
        # 创建按钮面板控件对象
        buttonPanel = ButtonPanel()

        self.addItem(buttonPanel.panel)
        # 缩放
        buttonPanel.panel.scale()
        buttonPanel.panel.setPos(70, 70)

        # self.animation = QPropertyAnimation(buttonPanel, 'pos')
        # self.animation.setDuration(3000)
        # self.animation.setStartValue(QPointF(70,70))
        # self.animation.setEndValue(QPointF(30,30))
        # self.animation.setEasingCurve(QEasingCurve.OutBounce)

        # self.animation = QPropertyAnimation(buttonPanel, 'rect')
        # self.animation.setDuration(3000)
        # self.animation.setStartValue(QRectF(-100,-100,200,200))
        # self.animation.setEndValue(QRectF(-50,-50,100,100))
        # self.animation.setEasingCurve(QEasingCurve.OutBounce)

        # 1. 创建一个动画对象, 并且设置目标 属性
        self.animation = QPropertyAnimation(buttonPanel)
        # 2. 动画时长
        self.animation.setDuration(3000)
        self.animation.setStartValue(QRectF(-65, -65, 130, 130))
        self.animation.setEndValue(QRectF(0, 0, 1, 1))
        self.animation.setEasingCurve(QEasingCurve.OutBounce)


class MyView(QGraphicsView):
    def __init__(self):
        super(MyView, self).__init__()

    def resizeEvent(self, event):
        """调整事件大小"""
        super(MyView, self).resizeEvent(event)
        """适合视口， 自动缩放"""
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)


if __name__ == '__main__':
    # 1.创建一个应用程序，传递命令行参数列表
    app = QApplication(sys.argv)

    # 2. 控件的操作
    # 创建控件,设置控件(大小,位置,样式...),事件,信号的处理
    # 2.1 创建控件
    # 当我们创建一个控件之后, 如果说,这个控件没有父控件, 则把它当做顶层控件(窗口)
    # 系统会自动的给窗口添加一些装饰(标题栏), 窗口控件具备一些特性(设置标题,图标)
    scene = MyScene()
    # 设定场景边框
    scene.setSceneRect(QRectF(-200, -200, 400, 400))
    # 创建视图控件
    w = MyView()
    # 场景对象传递给视图
    w.setScene(scene)
    w.show()
    sys.exit(app.exec_())
