# coding:utf-8

import sys
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

sample_data = [
    {'EventID': 0, 'EventType': 0, 'EventTypeName': 'level_config', 'EventArgs': {
        'player_spawns': ['hero_born'],
        'hero_id': 500101,
        'hero_dead_event_id': 170
    }},
    {'EventID': 1, 'EventType': 1, 'EventTypeName': 'trigger_events', 'EventArgs': {
        'event_ids': [31, 32, 33, 34, 35, 36, 37, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 55, 60, 63, 64,
                      67, 68, 69, 70, 71, 87, 88, 91, 92, 93, 96, 97, 98, 99, 100, 101],
        'ps': '总触发器',
        'only_once': 1
    }},
    {'EventID': 31, 'EventType': 39, 'EventTypeName': 'create_mechanism', 'EventArgs': {
        'spawn_point': 'zibao_chufa_1',
        'unit_type': 300601,
        'faction': 4,
        'mechanism_config_id': 1019,
        'mechanism_id': 'zibao_chufa',
        'related_mechanism': 'zibao_1'
    }},
    {'EventID': 32, 'EventType': 39, 'EventTypeName': 'create_mechanism', 'EventArgs': {
        'spawn_point': 'zibao_point_1',
        'unit_type': 410101,
        'faction': 4,
        'mechanism_config_id': 1020,
        'mechanism_id': 'zibao_1',
    }},
]


class Arrow(QGraphicsLineItem):
    def __init__(self, startItem, endItem, parent=None, scene=None):
        super(Arrow, self).__init__(parent, scene)

        self.arrowHead = QPolygonF()

        self.myStartItem = startItem
        self.myEndItem = endItem
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 1, Qt.SolidLine,
                         Qt.RoundCap, Qt.RoundJoin))

    def setColor(self, color):
        self.myColor = color

    def startItem(self):
        return self.myStartItem

    def endItem(self):
        return self.myEndItem

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super(Arrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def updatePosition(self):
        line = QLineF(self.mapFromItem(self.myStartItem, 0, 0), self.mapFromItem(self.myEndItem, 0, 0))
        self.setLine(line)

    def paint(self, painter, option, widget=None):
        if (self.myStartItem.collidesWithItem(self.myEndItem)):
            return

        myStartItem = self.myStartItem
        myEndItem = self.myEndItem
        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 10.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        centerLine = QLineF(myStartItem.pos(), myEndItem.pos())
        endPolygon = myEndItem.polygon()
        topLeft = endPolygon.last() + myEndItem.pos()
        p1 = endPolygon.last() + myEndItem.pos()

        intersectPoint = QPointF()
        for i in endPolygon:
            p2 = i + myEndItem.pos()
            polyLine = QLineF(p1, p2)
            intersectType = polyLine.intersect(centerLine, intersectPoint)
            if intersectType == QLineF.BoundedIntersection:
                break
            p1 = p2

        self.setLine(QLineF(intersectPoint, myStartItem.pos()))
        line = self.line()

        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p1() + QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                      math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p1() + QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                      math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.arrowHead.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QPen(myColor, 1, Qt.DashLine))
            myLine = QLineF(line)
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0, -8.0)
            painter.drawLine(myLine)


class DiagramItem(QGraphicsItem):
    currentId = 1

    def __init__(self, parent=None, title=None):
        super(DiagramItem, self).__init__(parent)

        self.setToolTip(
            "Click and drag this color onto the robot!"
        )

        self.title = '%s %d' % (title, DiagramItem.currentId)
        DiagramItem.currentId += 1
        self.headRect = QRect(-100, -50, 200, 30)
        self.bodyRect = QRect(-100, -20, 200, 70)

        self.arrows = []

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def polygon(self):
        return QPolygonF([
            self.headRect.topLeft(),
            self.bodyRect.bottomLeft(),
            self.bodyRect.bottomRight(),
            self.headRect.topRight()])

    def removeArrow(self, arrow):
        try:
            self.arrows.remove(arrow)
        except ValueError:
            pass

    def removeArrows(self):
        for arrow in self.arrows[:]:
            arrow.startItem().removeArrow(arrow)
            arrow.endItem().removeArrow(arrow)
            self.scene().removeItem(arrow)

    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def mousePressEvent(self, event):
        self.setCursor(Qt.ClosedHandCursor)

        super(DiagramItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super(DiagramItem, self).mouseMoveEvent(event)
        self.update()

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        super(DiagramItem, self).mouseReleaseEvent(event)

    def setTitle(self, text):
        self.title = text
        self.update()

    def boundingRect(self):
        return QRectF(-100, -50, 200, 100)

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            penWidth = 2
        else:
            penWidth = 1

        # 创建画笔对象
        pen = QPen()
        # 画笔对象属性设置
        pen.setColor(Qt.black)
        pen.setWidth(penWidth)

        # 把画笔设置给画师
        painter.setPen(pen)

        # 把背景刷设置给画师
        painter.setBrush(Qt.green)
        # 画师按路径画图
        painter.drawRect(self.headRect)
        # 创建字体对象
        font = QFont()
        if not self.title:
            self.title = 'Hello'
        # 画师写标题
        painter.drawText(self.headRect, Qt.AlignCenter, self.title)
        painter.setBrush(Qt.white)
        painter.drawRect(self.bodyRect)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.updatePosition()
        elif change == QGraphicsItem.ItemSelectedHasChanged:
            if self.isSelected():
                self.scene().itemSelected.emit(self)
            else:
                # print '%s is disselected' % self.title
                pass

        return value


class DiagramScene(QGraphicsScene):
    InsertItem, InsertLine, MoveItem = list(range(3))

    itemInserted = pyqtSignal(DiagramItem)
    itemSelected = pyqtSignal(QGraphicsItem)

    def __init__(self):
        super(DiagramScene, self).__init__()
        self.myMode = self.MoveItem
        self.myItemColor = Qt.white
        self.myLineColor = Qt.black
        self.line = None
        self.myFont = QFont()

    def setLineColor(self, color):
        self.myLineColor = color
        if self.isItemChange(Arrow):
            item = self.selectedItems()[0]
            item.setColor(self.myLineColor)
            self.update()

    def setItemColor(self, color):
        self.myItemColor = color
        if self.isItemChange(DiagramItem):
            item = self.selectedItems()[0]
            item.setBrush(self.myItemColor)

    def setItemTitle(self, title):
        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                item.setTitle(title)
                break

    def setMode(self, mode):
        self.myMode = mode

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        if self.myMode == self.InsertItem:
            item = DiagramItem(title='Monster')
            self.addItem(item)
            item.setPos(event.scenePos())
            self.itemInserted.emit(item)
        elif self.myMode == self.InsertLine:
            self.line = QGraphicsLineItem(QLineF(event.scenePos(),
                                                 event.scenePos()))
            self.addItem(self.line)
        elif self.myMode == self.MoveItem:
            mousePos = event.scenePos()
            item = self.itemAt(mousePos.x(), mousePos.y(), QTransform())

        super(DiagramScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.myMode == self.InsertLine and self.line:
            newLine = QLineF(self.line.line().p1(), event.scenePos())
            self.line.setLine(newLine)
        elif self.myMode == self.MoveItem:
            super(DiagramScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.myMode == self.InsertLine and self.line:
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)

            if len(startItems) and len(endItems) and \
                    isinstance(startItems[0], DiagramItem) and \
                    isinstance(endItems[0], DiagramItem) and \
                    startItems[0] != endItems[0]:
                startItem = startItems[0]
                endItem = endItems[0]
                arrow = Arrow(startItem, endItem)
                arrow.setColor(self.myLineColor)
                startItem.addArrow(arrow)
                endItem.addArrow(arrow)
                arrow.setZValue(-1000.0)
                self.addItem(arrow)
                arrow.updatePosition()
        elif self.myMode == self.MoveItem:
            mousePos = event.scenePos()
            item = self.itemAt(mousePos.x(), mousePos.y(), QTransform())

        self.line = None
        super(DiagramScene, self).mouseReleaseEvent(event)

    def isItemChange(self, type):
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False


class SidePanel(QWidget):
    # 声明带一个str类型参数的信号,并赋值给
    valueUpdated = pyqtSignal(str)

    def __init__(self):
        super(SidePanel, self).__init__()

        nameLabel = QLabel('Name')
        self.nameInput = QLineEdit('hello')

        changeButton = QPushButton('change')
        # 将信号clicked连接到指定槽函数
        changeButton.clicked.connect(self.changeClicked)
        # 表格布局管理器对象
        wlayout = QGridLayout()
        wlayout.addWidget(nameLabel, 0, 0)
        wlayout.addWidget(self.nameInput, 0, 1)
        wlayout.addWidget(changeButton, 1, 1)
        # 接收布局的父控件
        widget = QWidget()
        widget.setLayout(wlayout)

        # 总体布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(widget)
        self.setLayout(main_layout)

        # 设置最小宽度
        self.setMinimumWidth(200)

    def setModel(self, model):
        self.model = model

    def changeClicked(self):
        # 发射信号
        print("valueUpdated emit, value:", self.nameInput.text())
        self.valueUpdated.emit(self.nameInput.text())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # 在主窗口创建执行操作
        self.createActions()
        # 在主窗口创建工具条
        self.createToolBar()

        # 创建图形场景对象
        self.scene = DiagramScene()
        # 设置图形场景对象坐标和尺寸
        self.scene.setSceneRect(QRectF(0, 0, 5000, 5000))
        # 图形场景项目被选择，触发self.itemSelected方法
        self.scene.itemSelected.connect(self.itemSelected)

        # 创建图形视口对象，传递图形场景对象作为参数
        self.view = QGraphicsView(self.scene)
        # 创建侧边栏控件对象
        self.sidePanel = SidePanel()
        # 侧边栏值对象值更新信号，触发self.resetDiagramItemTitle方法
        self.sidePanel.valueUpdated.connect(self.resetDiagramItemTitle)

        # 创建水平布局对象
        layout = QHBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.sidePanel)

        # 创建父控件对象，用于布局
        self.main_widget = QWidget()
        # 把布局管理器对象设置给需要布局的父控件对象
        self.main_widget.setLayout(layout)
        # 在窗口中把主控件设置为中心控件
        self.setCentralWidget(self.main_widget)
        # 窗口标题
        self.setWindowTitle('Diagram Scene')

    def createActions(self):
        self.addAction = QAction(
            QIcon('./images/add.png'),
            '&Add item', self,
            shortcut='Ctrl++',
            statusTip='Add a new item',
            triggered=self.addNewItem)
        self.deleteAction = QAction(
            QIcon('./images/delete.png'),
            '&Delete item',
            self,
            shortcut='Delete',
            statusTip='Delete a item',
            triggered=self.deleteItem)

    def createToolBox(self):
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

        layout = QGridLayout()
        layout.addWidget()

    def createToolBar(self):
        self.editToolBar = self.addToolBar('Edit')
        self.editToolBar.addAction(self.deleteAction)
        # self.editToolBar.addAction(self.addAction)

        addButton = QToolButton()
        addButton.setCheckable(True)
        addButton.setIcon(QIcon('./images/add.png'))

        pointerButton = QToolButton()
        pointerButton.setCheckable(True)
        pointerButton.setChecked(True)
        pointerButton.setIcon(QIcon('./images/pointer.png'))
        linePointerButton = QToolButton()
        linePointerButton.setCheckable(True)
        linePointerButton.setIcon(QIcon('./images/linepointer.png'))

        self.pointerTypeGroup = QButtonGroup()
        self.pointerTypeGroup.addButton(addButton, DiagramScene.InsertItem)
        self.pointerTypeGroup.addButton(pointerButton, DiagramScene.MoveItem)
        self.pointerTypeGroup.addButton(linePointerButton, DiagramScene.InsertLine)
        self.pointerTypeGroup.buttonClicked[int].connect(self.pointerGroupClicked)

        # 场景比例组合盒
        self.sceneScaleCombo = QComboBox()
        self.sceneScaleCombo.addItems(['50%', '75%', '100%', '125%', '150%'])
        self.sceneScaleCombo.setCurrentIndex(2)
        self.sceneScaleCombo.currentIndexChanged[str].connect(self.sceneScaleChanged)

        self.pointerToolbar = self.addToolBar('Pointer type')
        self.pointerToolbar.addWidget(addButton)
        self.pointerToolbar.addWidget(pointerButton)
        self.pointerToolbar.addWidget(linePointerButton)
        self.pointerToolbar.addWidget(self.sceneScaleCombo)

    def addNewItem(self):
        self.scene.setMode(DiagramScene.InsertItem)

    def buttonGroupClicked(self, i):
        pass

    def itemSelected(self, item):
        pass

    def resetDiagramItemTitle(self, value):
        self.scene.setItemTitle(value)

    def deleteItem(self):
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                item.removeArrows()
            if isinstance(item, Arrow):
                startItem = item.startItem()
                startItem.removeArrow(item)
                endItem = item.endItem()
                endItem.removeArrow(item)
            self.scene.removeItem(item)

    def sceneScaleChanged(self, scale):
        """改变场景大小比列"""
        newScale = scale.left(scale.indexOf("%")).toDouble()[0] / 100.0
        oldMatrix = self.view.matrix()
        self.view.resetMatrix()
        self.view.translate(oldMatrix.dx(), oldMatrix.dy())
        self.view.scale(newScale, newScale)

    def pointerGroupClicked(self, i):
        self.scene.setMode(self.pointerTypeGroup.checkedId())


def main():
    # 1. 创建一个应用程序对象，传递命令行参数列表
    app = QApplication(sys.argv)

    # 2.1 创建顶层控件对象
    mainWindow = MainWindow()
    # 2.2 设置控件
    # 获取屏幕尺寸QRect(0， 0， 1440， 900）
    screenRect = app.desktop().screenGeometry()
    # 中心坐标点QPoint(719, 499) (599, 399)
    mainWindow.move(screenRect.center() - mainWindow.rect().center())
    # 2.3 展示控件
    mainWindow.show()
    mainWindow.setGeometry(100, 100, 1200, 800)
    # 3. 应用程序的执行, 进入到消息循环
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
