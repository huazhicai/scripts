import math
from PyQt5.QtCore import QPoint, QLine, pyqtSignal, QLineF, QRectF, QSizeF, Qt, QPointF
from PyQt5.QtGui import QFont, QTransform, QColor, QPen
from functools import cmp_to_key

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QMenu, QUndoStack
from controller import ControllerManager
from functools import partial

from test.editor import Arrow
from util import ItemType
from undo import CommandAdd, CommandDelete, CommandLink, CommandUnLink
from clipboard import GraphisClipboard
from mechan import mechanism
from collections import OrderedDict
from copy import deepcopy
from mutil import loadJsonData, dumpJsonData
import os

from graphics import DiagramItem, DiagramItemInput, DiagramItemOutput, DiagramItemRow, CosineLine, SelectionRect, \
    VirtualRect, CosineConnection, FreeCommentItem, ErrorRect, ConnectionBase


class QDMGraphicsScene(QGraphicsScene):
    itemSelected = pyqtSignal()
    itemsDeselected = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # self.scene = scene

        # settings
        self.gridSize = 20
        self.gridSquares = 5

        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)

    # the drag events won't be allowed until dragMoveEvent is overriden
    def dragMoveEvent(self, event):
        pass

    def setGrScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # here we create our grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if x % (self.gridSize * self.gridSquares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if y % (self.gridSize * self.gridSquares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)


class DiagramScene(QDMGraphicsScene):
    InsertItem, InsertLine, MoveItem, SelectItem = list(range(4))

    # itemInserted = pyqtSignal(DiagramItem)
    itemSelected = pyqtSignal(QGraphicsItem)
    cuteSignal = pyqtSignal(str)
    resetModeSignal = pyqtSignal()
    editSignal = pyqtSignal()

    def __init__(self, cKey):
        super(DiagramScene, self).__init__()
        self.controllerKey = cKey
        self.showDynamicMenu = True
        self.myMode = self.MoveItem
        self.myItemColor = Qt.white
        self.myLineColor = Qt.black
        self.line = None
        self.virtualRect = None
        self.selectRect = None
        self.errorRect = None
        self.selectPoint = None
        self.myFont = QFont()
        self.undoStack = QUndoStack(self)
        # 用户hash node id -> node的映射
        # 方便根据node id来查找到node
        self.cache = {}
        self.uuididxmap = {}
        self.isGlobal = None
        self.isRun = False

        self.breakPoints = []   # [uuid]

    def setUuidIdxMap(self, uuididx):
        self.uuididxmap = uuididx

    def createContextMenu(self):
        """创建右键菜单栏"""
        self.menu = QMenu()

        menuTreeData = ControllerManager().menuTree.tree
        self.genDynamicMenu(menuTreeData, self.menu)
        for submenu in self.menu.children()[1:]:
            if submenu.isEmpty():
                self.menu.removeAction(submenu.menuAction())

    def genDynamicMenu(self, data, parentMenu):
        for category in list(data.keys()):
            if type(data[category]) == OrderedDict:
                subMenu = parentMenu.addMenu(category)
                self.genDynamicMenu(data[category], subMenu)
            else:
                action_id = category
                action_name = data[category][0]
                action = parentMenu.addAction(action_name)
                action.triggered.connect(partial(self.chooseInsertItem, [action_name, action_id]))

    def contextMenuEvent(self, event):
        transform = QTransform(1, 0, 0, 0, 1, 0, 0, 0, 1)
        if self.itemAt(event.scenePos(), transform):
            QGraphicsScene.contextMenuEvent(self, event)
        else:
            if not self.showDynamicMenu:
                return
            self.menu.exec_(event.screenPos())
        super().contextMenuEvent(event)

    def chooseInsertItem(self, name):
        controller = ControllerManager().getController(self.controllerKey)
        controller.selectedItemType = ItemType(*name)
        self.setMode(DiagramScene.InsertItem)

    def cuteMessage(self, message):
        print('in cute')

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
            self.addDiagramItem(event.scenePos())
            if self.virtualRect is not None:
                self.removeItem(self.virtualRect)
            self.virtualRect = None
        elif self.myMode == self.InsertLine:
            # self.line = QGraphicsLineItem(QLineF( event.scenePos(),
            #	event.scenePos()))
            self.line = CosineLine(QLineF(event.scenePos(),
                                          event.scenePos()))
            self.addItem(self.line)
        elif self.myMode == self.MoveItem:
            mousePos = event.scenePos()
            item = self.itemAt(mousePos.x(), mousePos.y(), QTransform())

            if isinstance(item, DiagramItemOutput) or \
                    isinstance(item, DiagramItemRow):
                self.myMode = self.InsertLine
                self.line = CosineLine(QLineF(event.scenePos(),
                                              event.scenePos()))
                self.addItem(self.line)
            elif item is None:
                self.myMode = self.SelectItem
                self.selectPoint = event.scenePos()
                self.selectRect = SelectionRect(QRectF(self.selectPoint,
                                                       QSizeF(1, 1)))
                self.addItem(self.selectRect)

        super(DiagramScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.myMode == self.InsertLine and self.line:
            newLine = QLineF(self.line.line().p1(), event.scenePos())
            self.line.setLine(newLine)
        elif self.myMode == self.MoveItem:
            super(DiagramScene, self).mouseMoveEvent(event)
        elif self.myMode == self.InsertItem:
            if self.virtualRect is None:
                self.virtualRect = VirtualRect()
                self.addItem(self.virtualRect)
                self.virtualRect.setPos(event.scenePos())
            else:
                self.virtualRect.setPos(event.scenePos())
        elif self.myMode == self.SelectItem:
            v = event.scenePos() - self.selectPoint
            rect = QRectF(self.selectPoint, QSizeF(v.x(), v.y()))
            newRect = rect.normalized()
            self.selectRect.setRect(newRect)

    def mouseReleaseEvent(self, event):
        if self.myMode == self.InsertLine and self.line:
            startItems = self.items(self.line.line().p1())
            if len(startItems) and startItems[0] == self.line:
                startItems.pop(0)
            endItems = self.items(self.line.line().p2())
            if len(endItems) and endItems[0] == self.line:
                endItems.pop(0)

            self.removeItem(self.line)

            if len(startItems) and len(endItems) and startItems[0] != endItems[0]:
                # isinstance(startItems[0],DiagramItemRow) and \
                # isinstance(endItems[0],DiagramItemRow) and \
                # 此处由于连线的原因，
                # startItem 是Output
                # endItem 是 Input
                # 建立连接时，应该调换过来
                self.makeConnection(startItems[0], endItems[0])
            self.resetMode()
        elif self.myMode == self.MoveItem:
            mousePos = event.scenePos()
            item = self.itemAt(mousePos.x(), mousePos.y(), QTransform())
        elif self.myMode == self.SelectItem:
            if self.selectRect is not None:
                gitems = self.items(self.selectRect.rect(), Qt.IntersectsItemShape)

                hasSelects = False

                for gitem in gitems:
                    if isinstance(gitem, DiagramItem) or \
                            isinstance(gitem, CosineConnection) or \
                            isinstance(gitem, FreeCommentItem):
                        gitem.setSelected(True)
                        hasSelects = True

                if not hasSelects:
                    # 点选连线附近，可以选中连线
                    mousePos = event.scenePos()
                    topLeftPoint = QPointF(mousePos.x(), mousePos.y()) + QPointF(-5, -5)
                    tinyRect = QRectF(topLeftPoint, QSizeF(10, 10))
                    titems = self.items(tinyRect, Qt.IntersectsItemShape)
                    for titem in titems:
                        if isinstance(titem, CosineConnection):
                            titem.setSelected(True)

                self.removeItem(self.selectRect)
                self.resetMode()
                self.selectRect = None
                self.selectPoint = None

        self.line = None
        super(DiagramScene, self).mouseReleaseEvent(event)

    def resetMode(self):
        self.setMode(self.MoveItem)
        self.resetModeSignal.emit()

    def addDiagramItem(self, scenePos):
        controller = ControllerManager().getController(self.controllerKey)
        data = {'type': '%s' % controller.selectedItemType.typeId}
        data.update({
            'pos': {
                'x': scenePos.x(),
                'y': scenePos.y()
            }})
        command = CommandAdd(self, data)
        self.undoStack.push(command)

        # 跟踪计数
        ControllerManager().tracker.trackAdd(controller.selectedItemType.typeId)
        self.resetMode()

    def findAnyInputTypeSet(self, item):
        """
        找到
        """
        anyItemInputTypes = []
        for chItem in item.childItems():
            if isinstance(chItem, DiagramItemInput) and \
                    chItem.itemContent.contentType == 'Any':
                for arrow in chItem.arrows:
                    anyItemInputTypes.append(arrow.connectionType)

        return anyItemInputTypes if len(anyItemInputTypes) != 0 else None

    def makeConnection(self, startItem, endItem):
        """
        带Undo/Redo功能的建立连接
        """
        restrictValueTypes = None
        if startItem.itemContent.contentType == 'Any':
            # 搜索大节点的所有输入值，找到Any类型的输入的附带值类型集合
            restrictValueTypes = self.findAnyInputTypeSet(startItem.parentItem())
        # print 'restrictValueTypes', restrictValueTypes

        if not mechanism.canConnect(startItem, endItem, restrictValueTypes):
            return

        controller = ControllerManager().getController(self.controllerKey)
        if endItem.itemContent.contentType == 'Event':
            # Event，可以有任意多的入边
            edgeData = {
                'start': startItem.parentItem().uuid,
                'end': endItem.parentItem().uuid,
                'startItemTypeId': startItem.itemType.typeId,
                'endItemTypeId': endItem.itemType.typeId
            }

            command = CommandLink(self,
                                  [deepcopy(edgeData)],
                                  description='add a link')
            self.undoStack.push(command)
            self.editSignal.emit()

        else:
            # 别的类型，只能有一条入边
            # 且后续如果有别的边想要连入，必须删除之前连入的边
            if len(endItem.arrows) == 0:
                # 没有连入的边
                edgeData = {
                    'start': startItem.parentItem().uuid,
                    'end': endItem.parentItem().uuid,
                    'startItemTypeId': startItem.itemType.typeId,
                    'endItemTypeId': endItem.itemType.typeId
                }
                command = CommandLink(self, [deepcopy(edgeData)], description='add a link')
                self.undoStack.push(command)
                self.editSignal.emit()
            else:
                # 有连入的边，删除原来的边
                oldArrow = endItem.arrows[0]
                edgeData = {
                    'start': oldArrow.startItem().parentItem().uuid,
                    'end': oldArrow.endItem().parentItem().uuid,
                    'startItemTypeId': oldArrow.startItem().itemType.typeId,
                    'endItemTypeId': oldArrow.endItem().itemType.typeId
                }
                delCommand = CommandUnLink(self, [edgeData], description='remove an arrow')
                self.undoStack.push(delCommand)

                # 再添加新边
                arrow = CosineConnection(startItem, endItem)
                if startItem.itemContent.contentType != 'Any':
                    arrow.setConnectionType(startItem.itemContent.contentType)
                    arrow.setColor(startItem.itemContentColor)
                else:
                    arrow.setConnectionType(endItem.itemContent.contentType)
                    arrow.setColor(endItem.itemContentColor)
                # endItem.itemContent.contentValue = None
                edgeData = {
                    'start': arrow.startItem().parentItem().uuid,
                    'end': arrow.endItem().parentItem().uuid,
                    'startItemTypeId': arrow.startItem().itemType.typeId,
                    'endItemTypeId': arrow.endItem().itemType.typeId
                }
                command = CommandLink(self, [deepcopy(edgeData)], description='add a link')
                self.undoStack.push(command)
                self.editSignal.emit()

    def simpleMakeConnection(self, startItem, endItem):
        """
        不带Undo/Redo功能的建立连接，做必要的检查
        """
        if not mechanism.canConnect(startItem, endItem):
            return

        controller = ControllerManager().getController(self.controllerKey)

        if endItem.itemContent.contentType == 'Event':
            # Event，可以有任意多的入边
            self.directConnection(startItem, endItem)
        else:
            # 别的类型，只能有一条入边
            # 且后续如果有别的边想要连入，必须删除之前连入的边
            if len(endItem.arrows) == 0:
                # 没有连入的边
                self.directConnection(startItem, endItem)
            else:
                # 有连入的边，删除原来的边
                oldArrow = endItem.arrows[0]
                delCommand = CommandUnLink(controller,
                                           oldArrow,
                                           description='remove an arrow')
                self.undoStack.push(delCommand)

                # 在添加新边
                self.directConnection(startItem, endItem)
        self.editSignal.emit()

    def directConnection(self, startItem, endItem):
        """
        直接建立连接，不做任何检查
        """
        controller = ControllerManager().getController(self.controllerKey)

        arrow = CosineConnection(startItem, endItem)
        # print 'start type', startItem.itemContent.contentType
        if startItem.itemContent.contentType != 'Any':
            arrow.setConnectionType(startItem.itemContent.contentType)
            arrow.setColor(startItem.itemContentColor)
        else:
            arrow.setConnectionType(endItem.itemContent.contentType)
            arrow.setColor(endItem.itemContentColor)

        # controller.addEdge(startItem.parentItem(),
        # 		endItem.parentItem(),
        # 		startItem.itemType,
        # 		endItem.itemType,
        # 		startItem.itemContent.contentType)
        controller.addEdge(startItem.parentItem(),
                           endItem.parentItem(),
                           startItem.itemType,
                           endItem.itemType,
                           arrow.connectionType)
        startItem.addArrow(arrow)
        endItem.addArrow(arrow)
        arrow.setZValue(-1000.0)
        self.addItem(arrow)
        arrow.updatePosition()
        # 连线后不再具有值
        endItem.itemContent.contentValue = None
        startItem.update()
        endItem.update()

        self.editSignal.emit()

    def simpleDisconnection(self, arrow):
        """
        简单地删除连接，不包含Undo/Redo功能
        """
        controller = ControllerManager().getController(self.controllerKey)
        controller.removeEdge(arrow.startItem().parentItem(),
                              arrow.endItem().parentItem(),
                              arrow.startItem().itemType.typeId,
                              arrow.endItem().itemType.typeId)
        arrow.startItem().removeArrow(arrow)
        arrow.endItem().removeArrow(arrow)
        # 恢复默认值
        arrow.endItem().itemContent.contentValue = arrow.endItem().itemContent.defaultValue
        arrow.startItem().update()
        arrow.endItem().update()
        self.removeItem(arrow)

        self.editSignal.emit()

    def isItemChange(self, type):
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False

    def deleteSelectedItems(self):
        """
        删除所选择的items，先删除边，后删除节点，
        """
        edgesData = []
        controller = ControllerManager().getController(self.controllerKey)
        for item in self.selectedItems():
            if isinstance(item, ConnectionBase):
                if item.startItem().parentItem().isSelected() or item.endItem().parentItem().isSelected():
                    continue

                edgeData = {
                    'start': item.startItem().parentItem().uuid,
                    'end': item.endItem().parentItem().uuid,
                    'startItemTypeId': item.startItem().itemType.typeId,
                    'endItemTypeId': item.endItem().itemType.typeId
                }
                edgesData.append(edgeData)

        if len(edgesData) != 0:
            command = CommandUnLink(self, edgesData, description='remove an/several arrows')
            self.undoStack.push(command)

        itemDatasWithEdge = []

        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                itemData = self.itemToDataWithEdge(item)
                itemDatasWithEdge.append(itemData)
            elif isinstance(item, FreeCommentItem):
                controller.removeFreeComment(item)
                self.removeItem(item)

        if len(itemDatasWithEdge) != 0:
            command = CommandDelete(self,
                                    itemDatasWithEdge,
                                    description='delete an or serveral items')
            self.undoStack.push(command)

    def selectedItemsCenter(self):
        poses = []
        for item in self.selectedItems():
            poses.append(item.pos())

        if len(poses) == 0:
            return None

        avgx, avgy = 0.0, 0.0
        for p in poses:
            avgx += p.x()
            avgy += p.y()
        avgx /= len(poses)
        avgy /= len(poses)

        return QPointF(avgx, avgy)

    def selectedNodesCenter(self):
        # This function is to replace selectedItemsCenter in copy and past items
        # because selectedItemsCenter has two disadvantages:
        # 1.contains edges, which makes the center out of the cluster of nodes
        # 2.actually the result is not center, but the weight center
        xRange = []
        yRange = []
        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                pos = item.pos()
                xRange.append(pos.x())
                yRange.append(pos.y())
        if xRange:
            avgX = (min(xRange) + max(xRange)) / 2.0
            avgY = (min(yRange) + max(yRange)) / 2.0
        else:
            avgX = 0.0
            avgY = 0.0
        return QPointF(avgX, avgY)

    def selectedItemsBoundingRect(self):
        hasFlag = False
        xmin, xmax = 0.0, 0.0
        ymin, ymax = 0.0, 0.0
        for item in self.selectedItems():
            if isinstance(item, CosineConnection):
                continue

            hasFlag = True
            polygon = item.polygon()
            for i in [polygon[0], polygon[2]]:
                p = i + item.pos()
                if p.x() < xmin:
                    xmin = p.x()
                if p.x() > xmax:
                    xmax = p.x()
                if p.y() < ymin:
                    ymin = p.y()
                if p.y() > ymax:
                    ymax = p.y()

        if not hasFlag:
            return None

        return QRectF(QPointF(xmin, ymin), QSizeF(xmax - xmin,
                                                  ymax - ymin))

    def getSelectedNodes(self):
        nodes = []
        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                nodes.append(item)
        return nodes

    def cmp_(self, x, y):
        if x.depth < y.depth:
            return -1
        elif x.depth == y.depth:
            return 0
        else:
            return 1

    def _sortSelectedDiagramItemByDepth(self):
        selected = []
        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                selected.append(item)
        selected = sorted(selected, key=cmp_to_key(self.cmp_))
        # selected = sorted(selected, self.cmp_(x, y))
        return selected

    def copyItem(self):
        """
        拷贝项目
        1. 求得当前选中的所有项目的外接矩形的中心 center。
        2. 将选中的每个项目依次转化成带边数据itemDataWithEdge，
           转化数据时，利用center和item本身的位置计算出相对位置。
        """
        selected = []
        center = self.selectedNodesCenter()
        for item in self._sortSelectedDiagramItemByDepth():
            selected.append(self.itemToDataWithEdge(item, center))
        if len(selected) == 0:
            return

        for item in self.selectedItems():
            item.setSelected(False)

        itemDatasWithEdge = deepcopy(selected)

        GraphisClipboard().setGraphicsItems(itemDatasWithEdge)

    def cutItem(self):
        selected = []
        center = self.selectedItemsCenter()
        for item in self._sortSelectedDiagramItemByDepth():
            selected.append(self.itemToDataWithEdge(item, center))
        if len(selected) == 0:
            return

        GraphisClipboard().setGraphicsItems(selected)
        self.deleteSelectedItems()

    def pasteItem(self, mousePos=None):
        """
        粘贴项目
        从剪贴板中拿到带边的节点数据，替换原有id后，交给CommandAdd处理，
        """
        if not GraphisClipboard().hasGraphicsItems():
            return

        itemDatasWithEdge = GraphisClipboard().graphicsItems()

        controller = ControllerManager().getController(self.controllerKey)

        # 生成和替换id
        old2NewIds = {}
        for itemData in itemDatasWithEdge:
            oldId = itemData['node']['id']
            newId = controller.genUUID()
            old2NewIds[oldId] = newId

        self.replaceWithIdMap(itemDatasWithEdge, old2NewIds)

        command = CommandAdd(self,
                             itemDatasWithEdge,
                             description='add one/serveral items', mousePosition=mousePos)
        self.undoStack.push(command)

    def findSubItem(self, item, subItemTypeId):
        for subItem in item.childItems():
            if isinstance(subItem, DiagramItemInput) or isinstance(subItem, DiagramItemOutput):
                if subItem.itemType.typeId == subItemTypeId:
                    return subItem

        return None

    def replaceWithIdMap(self, itemDatasWithEdge, old2NewIds):
        for oldId, newId in list(old2NewIds.items()):
            # 替换入边中的 id
            for itemData in itemDatasWithEdge:
                inEdgesData = itemData['inEdgeData']
                outEdgeData = itemData['outEdgeData']

                for edgeData in inEdgesData:
                    if edgeData['start'] == oldId: edgeData['start'] = newId
                    if edgeData['end'] == oldId: edgeData['end'] = newId

                for edgeData in outEdgeData:
                    if edgeData['start'] == oldId: edgeData['start'] = newId
                    if edgeData['end'] == oldId: edgeData['end'] = newId

                if itemData['node']['id'] == oldId:
                    itemData['node']['id'] = newId

    def itemToData(self, item, center):
        controller = ControllerManager().getController(self.controllerKey)
        itemData = controller.nodeToData(item, center)

        return itemData

    def itemToDataWithEdge(self, item, center=None):
        controller = ControllerManager().getController(self.controllerKey)
        itemDataWithEdge = controller.nodeToDataWithEdge(item, center)

        return itemDataWithEdge

    def widerSelectedItems(self):
        boundingRect = self.selectedItemsBoundingRect()
        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                item.wider()

        if boundingRect is not None:
            self.update(boundingRect)

    def thinnerSelectedItems(self):
        boundingRect = self.selectedItemsBoundingRect()
        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                item.thinner()

        if boundingRect is not None:
            self.update(boundingRect)

    def commentSelectedItems(self):
        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                item.commentMe()

    def freeComment(self):
        view = self.views()[0]
        sz = view.size()
        width, height = sz.width(), sz.height()
        topLeft = view.mapToScene(0, 0)
        topLeftF = QPointF(topLeft.x(), topLeft.y())
        fCommentPos = topLeftF + QPointF(width / 3, height / 3)
        freec = FreeCommentItem('自由注释')
        self.addItem(freec)
        freec.setPos(fCommentPos)

        controller = ControllerManager().getController(self.controllerKey)
        controller.addFreeComment(freec)

    def foldSelectedItems(self):
        boundingRect = self.selectedItemsBoundingRect()

        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                item.fold()

        if boundingRect is not None:
            self.update(boundingRect)

    def unfoldSelectedItems(self):
        boundingRect = self.selectedItemsBoundingRect()

        for item in self.selectedItems():
            if isinstance(item, DiagramItem):
                item.unfold()

        if boundingRect is not None:
            self.update(boundingRect)

    def locateError(self, iD, subItemId):
        """
        定位导表错误的位置，并用红色矩形框将错误项框出
        """
        # 找到父节点
        if self.errorRect is None:
            self.errorRect = ErrorRect(QRectF(0, 0, 10, 10))
            self.addItem(self.errorRect)

        assert iD in self.cache, '%s not in item cache' % iD
        targetItem = self.cache[iD]
        for subItem in targetItem.childItems():
            if isinstance(subItem, DiagramItemInput) and subItem.itemType.typeId == subItemId:
                pos = subItem.scenePos()
                self.views()[0].centerOn(pos)
                self.errorRect.setRect(subItem.boundingRect())
                self.errorRect.setPos(pos)
                return

    def clearError(self):
        self.removeItem(self.errorRect)
        self.errorRect = None

    def locateFind(self, node):
        pos = node.scenePos()
        self.views()[0].centerOn(pos)
        node.setHighLight(1)

    def locateFindNode(self, prevNodeList, nextNodeList):
        for prevNode in prevNodeList:
            prevNode.setHighLight(2)
        for nextNode in nextNodeList:
            nextNode.setHighLight(2)

    def locateFindEdge(self, prevEdgeList, nextEdgeList):
        for edge in prevEdgeList:
            edge.setHighLight()
        for edge in nextEdgeList:
            edge.setHighLight()

    def clearFind(self, targetNode, prevNodeList, nextNodeList, prevEdgeList, nextEdgeList):
        if targetNode is None:
            return
        targetNode.removeHighLight()
        for prevNode in prevNodeList:
            prevNode.removeHighLight()
        for nextNode in nextNodeList:
            nextNode.removeHighLight()
        for prevEdge in prevEdgeList:
            prevEdge.removeHighLight()
        for nextEdge in nextEdgeList:
            nextEdge.removeHighLight()

    def addToCache(self, item):
        if item.uuid not in self.cache:
            self.cache[item.uuid] = item
        else:
            print(item.uuid, 'already existes in scene')

    def removeFromCache(self, item):
        if item.uuid in self.cache:
            del self.cache[item.uuid]
        else:
            print('error', item.uuid, 'do not exist in scene')


class TemplateScene(QDMGraphicsScene):
    MoveItem, SelectItem = list(range(2))

    itemSelected = pyqtSignal(QGraphicsItem)
    editSignal = pyqtSignal()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.showDynamicMenu = True
        self.virtualRect = None
        self.selectRect = None
        self.selectPoint = None
        self.myMode = self.MoveItem

        self.autoGenAndLayoutMetaItems()

    def autoGenAndLayoutMetaItems(self):
        nodesDefData = loadJsonData('meta/nodes.json')
        if os.path.exists('meta/template.json'):
            self.templateData = loadJsonData('meta/template.json')
        else:
            self.templateData = {}

        leftMark = QPointF(-2000, -2050)
        topLeft = QPointF(-2000, -2050)
        lastCategory = None
        lastMaxHeight = 0

        for nodeDef in nodesDefData:
            category = nodeDef['category']
            if category != lastCategory:
                leftMark = leftMark + QPointF(0, lastMaxHeight + 50)
                topLeft = leftMark
                lastCategory = category
                lastMaxHeight = 0

            item = self.addDiagramItem(nodeDef)
            itemRect = item.boundingRect()
            w, h = itemRect.width(), itemRect.height()
            item.setPos(topLeft + QPointF(w / 2, h / 2))
            if h > lastMaxHeight:
                lastMaxHeight = h

            topLeft = topLeft + QPoint(w + 30, 0)

    def saveTemplate(self):
        dumpJsonData('meta/template.json', self.templateData)

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        mousePos = event.scenePos()
        item = self.itemAt(mousePos.x(), mousePos.y(), QTransform())

        if item is None:
            self.myMode = self.SelectItem
            self.selectPoint = event.scenePos()
            self.selectRect = SelectionRect(QRectF(self.selectPoint,
                                                   QSizeF(1, 1)))
            self.addItem(self.selectRect)

        super(self.__class__, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.myMode == self.MoveItem:
            super(self.__class__, self).mouseMoveEvent(event)
        elif self.myMode == self.SelectItem:
            v = event.scenePos() - self.selectPoint
            rect = QRectF(self.selectPoint, QSizeF(v.x(), v.y()))
            newRect = rect.normalized()
            self.selectRect.setRect(newRect)

    def mouseReleaseEvent(self, event):
        if self.myMode == self.MoveItem:
            mousePos = event.scenePos()
            item = self.itemAt(mousePos.x(), mousePos.y(), QTransform())
        elif self.myMode == self.SelectItem:
            if self.selectRect is not None:
                gitems = self.items(self.selectRect.rect(), Qt.IntersectsItemShape)

                hasSelects = False

                for gitem in gitems:
                    if isinstance(gitem, DiagramItem) or \
                            isinstance(gitem, FreeCommentItem):
                        gitem.setSelected(True)
                        hasSelects = True

                self.removeItem(self.selectRect)
                self.resetMode()
                self.selectRect = None
                self.selectPoint = None

        self.line = None
        super(self.__class__, self).mouseReleaseEvent(event)

    def resetMode(self):
        self.myMode = self.MoveItem

    def addDiagramItem(self, data):
        item = DiagramItem(data=data, mode='template')
        self.addItem(item)

        return item

    def updateItemTextNote(self, typeId, note):
        assert type(note) == list
        print('update note for ', typeId, note)
        self.templateData[typeId] = note
        self.editSignal.emit()

    def getNoteText(self, typeId):
        note = self.templateData.get(typeId, None)
        return note[0] if note is not None else ''

    def getNote(self, typeId):
        return self.templateData.get(typeId, None)
