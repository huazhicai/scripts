# coding:utf-8、
import time

import math
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSizeF, QRectF, QLineF, QPointF, pyqtSignal, QSize
from PyQt5.QtGui import QPen, QPainter, QPainterPath, QPolygonF, QPixmap, QColor, QLinearGradient

from util import interpolate_cosine_points, editable_types, ItemType, ItemContent, Vec3
from colors import ColorManager
from dlg import ChangeValueDialog, TemplateDialog
from font import FontManager, measureWidth
from mutil import resource_path


class LineBase(QGraphicsLineItem):
    def __init__(self, line, parent=None):
        super(LineBase, self).__init__(line, parent)
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 1, Qt.SolidLine,
                         Qt.RoundCap, Qt.RoundJoin))


class ArrowLine(LineBase):
    def __init__(self, line, parent=None):
        super(ArrowLine, self).__init__(line, parent)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)

        painter.setPen(self.pen())
        painter.drawLine(self.line)


class CosineLine(LineBase):
    def __init__(self, line, parent=None):
        super(CosineLine, self).__init__(line, parent)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)

        painter.setPen(self.pen())

        path = QPainterPath()
        p1 = self.line().p1()
        p2 = self.line().p2()
        path.moveTo(p1.x(), p1.y())
        for p in interpolate_cosine_points(p1.x(), p1.y(), p2.x(), p2.y()):
            path.lineTo(p[0], p[1])
        painter.drawPath(path)


class ConnectionBase(QGraphicsLineItem):
    def __init__(self, startItem, endItem, parent=None, scene=None):
        super(ConnectionBase, self).__init__(parent)

        self.myStartItem = startItem
        self.myEndItem = endItem
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 1, Qt.SolidLine,
                         Qt.RoundCap, Qt.RoundJoin))
        self.connectionType = ''

        self.tempColor = None

        # to reduce the complexity of calcaute line pos
        self.changedPos = True
        self.start = QPointF(0.0, 0.0)
        self.end = QPointF(0.0, 0.0)

    def setConnectionType(self, cType):
        self.connectionType = cType

    # if self.connectionType == 'Unit':
    #	self.setColor(Qt.green)
    # elif self.connectionType == 'Event':
    #	self.setColor(Qt.black)

    def setHighLight(self):
        self.tempColor = self.myColor
        self.myColor = Qt.white
        self.setPen(QPen(self.myColor, 3, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))

    def removeHighLight(self):
        self.myColor = self.tempColor
        self.setPen(QPen(self.myColor, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

    def setColor(self, color):
        self.myColor = color

    def startItem(self):
        return self.myStartItem

    def endItem(self):
        return self.myEndItem

    def updatePosition(self):
        if isinstance(self.myStartItem, DiagramItemRow):
            spos = self.mapFromItem(self.myStartItem, self.myStartItem.rcenter())
        else:
            spos = self.mapFromItem(self.myStartItem, self.myStartItem.center())

        if isinstance(self.myEndItem, DiagramItemRow):
            epos = self.mapFromItem(self.myEndItem, self.myEndItem.lcenter())
        else:
            epos = self.mapFromItem(self.myEndItem, self.myEndItem.center())

        absStart = spos - self.start
        absEnd = epos - self.end
        self.changedPos = False
        if abs(absStart.x()) > 1 or abs(absStart.y()) > 1:
            self.start = spos
            self.changedPos = True
        if abs(absEnd.x()) > 1 or abs(absEnd.y()) > 1:
            self.end = epos
            self.changedPos = True

        self.setLine(QLineF(spos, epos))


class ArrowConnection(ConnectionBase):
    def __init__(self, startItem, endItem, parent=None, scene=None):
        super(ArrowConnection, self).__init__(startItem, endItem,
                                              parent, scene)

        self.arrowHead = QPolygonF()

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super(ArrowConnection, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def paint(self, painter, option, widget=None):
        if (self.myStartItem.collidesWithItem(self.myEndItem)):
            return

        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.isSelected():
            penWidth = 3
        else:
            penWidth = 1

        myStartItem = self.myStartItem
        myEndItem = self.myEndItem
        myColor = self.myColor
        myPen = self.pen()
        myPen.setWidth(penWidth)
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


class CosineConnection(ConnectionBase):
    def __init__(self, startItem, endItem, parent=None, scene=None):
        super(CosineConnection, self).__init__(startItem, endItem,
                                               parent)
        self.path = None

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        if not self.path or self.changedPos:
            path = QPainterPath()
            p1 = self.line().p1()
            p2 = self.line().p2()
            path.moveTo(p1.x(), p1.y())
            for p in interpolate_cosine_points(p1.x(), p1.y(), p2.x(), p2.y()):
                path.lineTo(p[0], p[1])
            self.path = path
        return self.path

    def paint(self, painter, option, widget=None):
        if (self.myStartItem.collidesWithItem(self.myEndItem)):
            return
        self.updatePosition()

        if self.changedPos or not self.path:
            self.path = self.shape()

        if self.isSelected():
            penWidth = 4
        else:
            penWidth = 2

        painter.setRenderHint(QPainter.Antialiasing, True)

        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        myPen.setWidth(penWidth)
        painter.setPen(myPen)

        painter.drawPath(self.path)


class DiagramItemBase(QGraphicsItem):
    def __init__(self, parent=None, scene=None, itemType=None, itemContent=None):
        super(DiagramItemBase, self).__init__(parent)
        self.arrows = []
        self.breakPoints = []
        self.itemType = itemType
        if itemContent is not None and itemContent.contentValue is not None:
            self.title = '%s:%s' % (itemType.typeName, itemContent.contentValue)
        else:
            self.title = itemType.typeName

        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

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

    def setTitle(self, text):
        self.title = text
        self.update()

    def mousePressEvent(self, event):
        # self.setCursor(Qt.ClosedHandCursor)
        super(DiagramItemBase, self).mousePressEvent(event)

    # def mouseMoveEvent(self,event):
    #	super(DiagramItemBase,self).mouseMoveEvent(event)
    #	self.update()

    def mouseReleaseEvent(self, event):
        # self.setCursor(Qt.OpenHandCursor)
        super(DiagramItemBase, self).mouseReleaseEvent(event)


class DiagramItem(DiagramItemBase):
    Width = 190

    def __init__(self, parent=None, scene=None, data=None, mode='normal', depth=0):
        assert data is not None, 'init data of DiagramItem is None'

        self.data = data
        self.mode = mode

        self.maxWidth = 0

        # to solve overlap of item
        self.depth = depth

        super(DiagramItem, self).__init__(parent=parent, scene=scene,
                                          itemType=ItemType(*(data['name'])))
        self.setAcceptHoverEvents(True)

        self.maxWidth = measureWidth(self.title)

        if data.get('deltaWidth', None) is not None:
            self.deltaWidth = data['deltaWidth']
        else:
            self.deltaWidth = 0

        self.Width += self.deltaWidth

        self.isFold = False
        self.unfoldItem = None

        self.computeGeometry()

        self.setToolTip(
            "Click title to select and move this item!"
        )

        self.headBackgroundColor = ColorManager().getColor('head', data['category'])
        self.bodyBackgroundColor = ColorManager().getColor('body', data['category'])

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.initSubItems()
        self.comment = None

        self.highLightFlag = 0
        self.nodeType = 0

        self.hasBreakPoint = False

    def computeGeometry(self):
        if self.isFold:
            # 按照折叠的情形来计算坐标
            self.computeFoldedGeometry()
        else:
            # 按照非折叠的情形来计算坐标
            self.computeNormalGeometry()

    def computeFoldedGeometry(self):
        headHeight = 30
        bodyHeight = 0
        outYs = []
        inputYs = []
        eventYs = []
        cY = headHeight

        if self.data is not None:
            cY += 15
            bodyHeight += 25

            if self.data.get('args', None) != None:
                for mp in self.data['args']:
                    inputYs.append(cY)

                    param_name, param_default = mp['name'], mp.get('default', None)
                    if param_default is None:
                        self.maxWidth = max(self.maxWidth,
                                            measureWidth(param_name[0]))
                    else:
                        self.maxWidth = max(self.maxWidth,
                                            measureWidth('%s:%s' % (param_name[0], str(param_default))))

            if self.data.get('function', None) != None and \
                    type(self.data['function']) == str:
                for mp in self.data.get('function'):
                    eventYs.append(cY)

            if self.data.get('returns', None) != None:
                for mp in self.data.get('returns'):
                    outYs.append(cY)
                    param_name = mp['name']
                    self.maxWidth = max(self.maxWidth,
                                        measureWidth(param_name[0]))
        else:
            cY += 15
            bodyHeight += 25
            eventYs.append(cY)

        bodyHeight += 5

        totalHeight = headHeight + bodyHeight

        self.bodyHeight = bodyHeight
        self.headHeight = headHeight
        self.totalHeight = totalHeight

        center = QPointF(0, 0)
        self.headTopLeft = center - QPointF(self.Width / 2.0, totalHeight / 2.0)
        self.bodyTopLeft = self.headTopLeft + QPointF(0, headHeight)

        self.outCenters = []
        self.eventCenters = []
        self.inputCenters = []

        outX = self.headTopLeft.x() + self.Width - DiagramItemOutput.MarginRight - DiagramItemOutput.OutputWidth / 2.0
        for y in outYs:
            self.outCenters.append(QPointF(outX, y - totalHeight / 2.0))

        eventX = self.headTopLeft.x() + DiagramItemInput.InputWidth / 2.0 + DiagramItemInput.MarginLeft
        for y in eventYs:
            self.eventCenters.append(QPointF(eventX, y - totalHeight / 2.0))
        inputX = self.headTopLeft.x() + DiagramItemInput.InputWidth / 2.0 + DiagramItemInput.MarginLeft
        for y in inputYs:
            self.inputCenters.append(QPointF(inputX, y - totalHeight / 2.0))

        self.headRect = QRectF(self.headTopLeft,
                               QSizeF(self.Width, self.headHeight))
        self.bodyRect = QRectF(self.bodyTopLeft,
                               QSizeF(self.Width, self.bodyHeight))

    def computeNormalGeometry(self):
        headHeight = 30
        bodyHeight = 0
        outYs = []
        inputYs = []
        eventYs = []
        cY = headHeight
        if self.data is not None:

            # 输出节点的中心y坐标
            isFirst = True

            # 为默认Input预留的空间, query类型的节点不能有Input
            # if not query:
            #	bodyHeight += 25
            #	cY += 15 if isFirst else 25
            #	isFirst = False
            #	inputYs.append(cY)

            # if not query and self.data.get('args',None) != None:
            # 纵向计算item的纵坐标
            # 在读取输入和输出数据时，需要根据字符串计算出其文字占用的宽度
            if self.data.get('args', None) != None:
                for mp in self.data['args']:
                    bodyHeight += 25
                    cY += 15 if isFirst else 25
                    isFirst = False
                    inputYs.append(cY)

                    param_name, param_default = mp['name'], mp.get('default', None)
                    if param_default is None:
                        self.maxWidth = max(self.maxWidth, measureWidth(param_name[0]))
                    else:
                        self.maxWidth = max(self.maxWidth,
                                            measureWidth('%s:%s' % (param_name[0], str(param_default))))

            if self.data.get('function', None) != None and \
                    type(self.data['function']) == list:
                for mp in self.data['function']:
                    bodyHeight += 25
                    cY += 15 if isFirst else 25
                    isFirst = False
                    eventYs.append(cY)

            if self.data.get('returns', None) != None:
                for mp in self.data['returns']:
                    bodyHeight += 25
                    cY += 15 if isFirst else 25
                    isFirst = False
                    outYs.append(cY)
                    param_name = mp['name']
                    self.maxWidth = max(self.maxWidth, measureWidth(param_name[0]))

        # 给默认Out的空间
        # bodyHeight += 25
        # cY += 15 if isFirst else 25
        # isFirst = False
        # outYs.append(cY)
        else:
            cY += 25
            eventYs.append(cY)

        bodyHeight += 5

        totalHeight = headHeight + bodyHeight

        self.bodyHeight = bodyHeight
        self.headHeight = headHeight
        self.totalHeight = totalHeight

        center = QPointF(0, 0)
        self.headTopLeft = center - QPointF(self.Width / 2.0, totalHeight / 2.0)
        self.bodyTopLeft = self.headTopLeft + QPointF(0, headHeight)

        self.outCenters = []
        self.eventCenters = []
        self.inputCenters = []

        outX = self.headTopLeft.x() + self.Width - DiagramItemOutput.MarginRight - DiagramItemOutput.OutputWidth / 2.0
        for y in outYs:
            self.outCenters.append(QPointF(outX, y - totalHeight / 2.0))
        # eventX = self.headTopLeft.x() + self.Width/2.0
        eventX = self.headTopLeft.x() + DiagramItemInput.InputWidth / 2.0 + DiagramItemInput.MarginLeft
        for y in eventYs:
            self.eventCenters.append(QPointF(eventX, y - totalHeight / 2.0))
        inputX = self.headTopLeft.x() + DiagramItemInput.InputWidth / 2.0 + DiagramItemInput.MarginLeft
        for y in inputYs:
            self.inputCenters.append(QPointF(inputX, y - totalHeight / 2.0))

        self.headRect = QRectF(self.headTopLeft,
                               QSizeF(self.Width, self.headHeight))
        self.bodyRect = QRectF(self.bodyTopLeft,
                               QSizeF(self.Width, self.bodyHeight))

    def initSubItems(self):
        # self.subitems = []
        category = self.data['category']
        query = self.data.get('query', False)

        # 默认的Input对象
        # if not query:
        #	param_name,param_type = 'Input','Event'
        #	subitem = DiagramItemInput(parent=self,
        #		itemType=ItemType(param_name,'InputId'),
        #		itemContent=ItemContent(param_type,None))
        #	subitem.setPos(self.inputCenters[-1])

        hasEvent = False

        # if not query and self.data.get('args',None) != None:
        if self.data.get('args', None) != None:
            i = 0
            for mp in self.data['args']:
                param_name, param_type, param_default = mp['name'], mp['type'], mp.get('default', None)
                if param_type == 'Event':
                    hasEvent = True
                if param_type == 'Vec3' and param_default is not None:
                    param_default = Vec3.valueFromString(param_default)
                subitem = DiagramItemInput(parent=self,
                                           itemType=ItemType(*param_name),
                                           itemContent=ItemContent(param_type, param_default),
                                           deltaWidth=self.deltaWidth)
                subitem.setPos(self.inputCenters[i])
                # self.subitems.append(subitem)
                i += 1

        if self.data.get('function', None) != None and \
                type(self.data['function']) == list:
            i = 0
            for mp in self.data['function']:
                event_name, event_type = mp[0], 'Event'
                subitem = DiagramItemInput(parent=self,
                                           itemType=ItemType(event_name, event_type),
                                           itemContent=ItemContent(event_type, None),
                                           deltaWidth=self.deltaWidth)
                subitem.setPos(self.eventCenters[i])
                # self.subitems.append(subitem)
                i += 1

        if self.data.get('returns', None) != None:
            i = 0
            for mp in self.data['returns']:
                param_name, param_type, param_default = mp['name'], mp['type'], mp.get('default', None)
                subitem = DiagramItemOutput(parent=self,
                                            itemType=ItemType(*param_name),
                                            itemContent=ItemContent(param_type, param_default),
                                            deltaWidth=self.deltaWidth)
                subitem.setPos(self.outCenters[i])
                # self.subitems.append(subitem)
                i += 1

        if query and hasEvent:
            # 给出有query，不能有Input的警告，提示进行修改
            QMessageBox.warning(None,
                                'Warning',
                                'query类型的节点不能有Event类型输入，请修改' + self.title,
                                QMessageBox.Ok)

        while self.Width < self.maxWidth + 2 * DiagramItemInput.MarginLeft +\
                DiagramItemInput.InputWidth + DiagramItemInput.ImageWidth:
            self.wider()

    # 默认的Out对象
    # param_name,param_type = 'Out','Event'
    # subitem = DiagramItemOutput(parent=self,
    #	itemType=ItemType(param_name,'OutputId'),
    #	itemContent=ItemContent(param_type,None))
    # subitem.setPos(self.outCenters[0])

    def updateSubItems(self, flag):
        iIn, iOut = 0, 0
        for subitem in self.childItems():
            if isinstance(subitem, DiagramItemInput):
                # 更新输入变量的pos
                if flag == 'wider':
                    subitem.wider()
                elif flag == 'thinner':
                    subitem.thinner()
                subitem.setPos(self.inputCenters[iIn])
                iIn += 1
            elif isinstance(subitem, DiagramItemOutput):
                # 更新输出变量的位置
                if flag == 'wider':
                    subitem.wider()
                elif flag == 'thinner':
                    subitem.thinner()
                subitem.setPos(self.outCenters[iOut])
                iOut += 1
            elif isinstance(subitem, DiagramItemUnfold):
                # 更新展开按钮控件的位置
                if flag == 'wider':
                    subitem.wider()
                elif flag == 'thinner':
                    subitem.thinner()

    def setUUID(self, iD):
        self.uuid = iD

    def updateContentValues(self, args):
        for subitem in self.childItems():
            if isinstance(subitem, DiagramItemInput):
                if subitem.itemType.typeId in args:
                    subitem.itemContent.contentValue = args[subitem.itemType.typeId]
                    subitem.setTitle(subitem.itemType.typeName + ': '
                                     + str(subitem.itemContent.contentValue))

    def setHeadBackground(self, color):
        self.headBackgroundColor = color

    def setBodyBackground(self, color):
        self.bodyBackgroundColor = color

    def polygon(self):
        return QPolygonF([
            self.headRect.topLeft(),
            self.bodyRect.bottomLeft(),
            self.bodyRect.bottomRight(),
            self.headRect.topRight()])

    def headBackground(self):
        return self._headBackgroundColor

    def bodyBackground(self):
        return self._bodyBackgroundColor

    def boundingRect(self):
        return QRectF(self.headTopLeft,
                      QSizeF(self.Width, self.totalHeight))

    def setHighLight(self, nodeTp):
        self.highLightFlag = 1
        self.nodeType = nodeTp
        self.update()

    def removeHighLight(self):
        self.highLightFlag = 0
        self.nodeType = 0
        self.update()

    def paint(self, painter, option, widget=None):
        pen = QPen()
        if self.highLightFlag == 1:
            if self.nodeType == 1:  # 主节点高亮
                lineColor = Qt.yellow
            elif self.nodeType == 2:
                lineColor = Qt.red  # 异常节点高亮
            else:  # 前驱节点和后继节点高亮
                lineColor = Qt.white
            pen.setStyle(Qt.DashLine)
            pen.setWidth(3)
        elif self.isSelected() == True:
            lineColor = Qt.white
            pen.setStyle(Qt.SolidLine)
            pen.setWidth(1)
        else:
            lineColor = None
            pen.setStyle(Qt.SolidLine)
            pen.setWidth(1)

        painter.setRenderHint(QPainter.Antialiasing, True)  # 抗锯齿, 防止图形走样

        # head
        if lineColor is None:
            pen.setColor(self.headBackgroundColor)
        else:
            pen.setColor(lineColor)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(self.headBackgroundColor)
        painter.drawRect(self.headRect)

        # body
        if lineColor is None:
            pen.setColor(self.bodyBackgroundColor)
        else:
            pen.setColor(lineColor)
        painter.setPen(pen)
        painter.setBrush(self.bodyBackgroundColor)
        painter.drawRect(self.bodyRect)

        # 设置标题文本的颜色
        pen.setColor(Qt.white)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setFont(FontManager().customFont())
        painter.drawText(self.headRect,
                         Qt.AlignCenter,
                         self.title)

    def hoverMoveEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.updateCommentPosition()
            # self.scene().editSignal.emit()
            for arrow in self.arrows:
                arrow.updatePosition()
        elif change == QGraphicsItem.ItemSelectedHasChanged:
            if self.isSelected():
                self.scene().itemSelected.emit(self)
            else:
                pass

        return value

    def updateCommentPosition(self):
        if self.comment is not None:
            sPos = self.scenePos()
            topLeft = self.headRect.topLeft() + sPos
            newCommentPos = topLeft + QPointF(0, -30)
            self.comment.setPos(newCommentPos)

    def setComment(self, comment):
        self.comment = comment

    def wider(self):
        self.Width += 20
        self.deltaWidth += 20
        self.computeGeometry()
        self.updateSubItems('wider')
        self.update()

    def thinner(self):
        if self.Width <= 190:
            return

        self.Width -= 20
        self.deltaWidth -= 20
        self.computeGeometry()
        self.updateSubItems('thinner')
        self.update()

    def fold(self):
        if self.isFold:
            return

        self.isFold = True
        self.computeGeometry()
        self.updateSubItems('fold')

        # 加上展开按钮
        self.unfoldItem = DiagramItemUnfold(parent=self,
                                            deltaWidth=self.deltaWidth)
        unfoldX = self.headTopLeft.x() + self.Width / 2.0
        if len(self.inputCenters) == 0:
            self.unfoldItem.setPos(QPointF(unfoldX,
                                           self.outCenters[0].y()))
        else:
            self.unfoldItem.setPos(QPointF(unfoldX,
                                           self.inputCenters[0].y()))

        self.update()
        self.updateCommentPosition()

    def unfold(self):
        if not self.isFold:
            return

        self.isFold = False
        self.computeGeometry()
        self.updateSubItems('unfold')

        # 去除展开按钮
        self.scene().removeItem(self.unfoldItem)
        self.unfoldItem = None

        self.update()
        self.updateCommentPosition()

    def mouseDoubleClickEvent(self, event):
        if self.comment is not None:
            return

        self.commentMe()

    def commentMe(self):
        topLeft = self.headTopLeft + self.scenePos()
        commentPos = topLeft + QPointF(0, -30)
        commentItem = CommentItem('注释此项目')
        self.setComment(commentItem)
        self.scene().addItem(commentItem)
        commentItem.setPos(commentPos)

    def getArgsTypeAndValue(self, argName):
        for item in self.childItems():
            if isinstance(item, DiagramItemInput):
                if item.itemType.typeName == argName:
                    return item.itemContent.contentType, item.itemContent.contentValue
        return None, None

    def getInputItemByName(self, itemName):
        for item in self.childItems():
            if isinstance(item, DiagramItemInput):
                if item.itemType.typeName == itemName:
                    return item
        return None


class DiagramItemRow(DiagramItemBase):
    InputWidth, InputHeight = 20, 20
    OutputWidth, OutputHeight = 20, 20
    TitleWidth, TitleHeight = 120, 20
    MarginTop, MarginLeft = 10, 10

    def __init__(self, parent=None, scene=None, itemType=None, itemContent=None):
        super(DiagramItemRow, self).__init__(parent, scene, itemType, itemContent)

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.itemContent = itemContent

        center = QPointF(0, 0)
        self.titleTopLeft = center - QPointF(self.TitleWidth / 2.0, self.TitleHeight / 2.0)
        self.inputTopLeft = self.titleTopLeft - QPointF(self.MarginLeft + self.InputWidth, 0)
        self.inputCenter = self.inputTopLeft + QPointF(self.InputWidth / 2.0, self.InputHeight / 2.0)
        self.outputTopLeft = self.titleTopLeft + QPointF(self.MarginLeft + self.TitleWidth, 0)
        self.outputCenter = self.outputTopLeft + QPointF(self.OutputWidth / 2.0, self.OutputHeight / 2.0)

        self.inputRect = QRectF(self.inputTopLeft, QSizeF(self.InputWidth, self.InputHeight))
        self.outputRect = QRectF(self.outputTopLeft, QSizeF(self.OutputWidth, self.OutputHeight))
        self.centerRect = QRectF(self.titleTopLeft, QSizeF(self.TitleWidth, self.TitleHeight))

    def center(self):
        return QPointF(0, 0)

    def lcenter(self):
        return self.inputCenter

    def rcenter(self):
        return self.outputCenter

    def polygon(self):
        rect = self.boundingRect()
        return QPolygonF([
            rect.topLeft(),
            rect.bottomLeft(),
            rect.bottomRight(),
            rect.topRight()])

    def boundingRect(self):
        return QRectF(self.inputTopLeft,
                      QSizeF(self.InputWidth + self.OutputWidth + self.TitleWidth + 2 * self.MarginLeft,
                             self.InputWidth))

    def paint(self, painter, option, widget=None):
        lineColor = Qt.yellow

        painter.setRenderHint(QPainter.Antialiasing, True)

        penWidth = 10
        pen = QPen()
        pen.setColor(lineColor)
        pen.setWidth(penWidth)
        pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(pen)

        painter.drawRect(self.centerRect)

        leftRect = self.inputRect
        painter.setBrush(Qt.yellow)
        painter.drawRect(leftRect)

        rightRect = self.outputRect
        painter.setBrush(Qt.blue)
        # painter.drawRect(rightRect)
        painter.drawText(self.centerRect,
                         # Qt.AlignCenter,
                         self.title)

    def mouseDoubleClickEvent(self, event):
        super(DiagramItemRow, self).mouseDoubleClickEvent(event)


class DiagramItemInput(DiagramItemBase):
    InputWidth, InputHeight = 20, 20
    TitleWidth, TitleHeight = 130, 20
    ImageWidth, ImageHeight = 20, 20
    breakPointWidth, breakPointHeight = 20, 20
    MarginLeft = 5
    MarginTop = 10

    def __init__(self, parent=None, scene=None, itemType=None, itemContent=None, deltaWidth=0):
        super(DiagramItemInput, self).__init__(parent, scene,
                                               itemType, itemContent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setAcceptHoverEvents(True)

        self.TitleWidth += deltaWidth

        self.computeGeometry()

        self.itemContentColor = ColorManager().getColor('data', itemContent.contentType)

        self.itemContent = itemContent
        self.imageSourceRect = QRectF(0, 0, self.ImageWidth, self.ImageHeight)
        # self.pixmap = QPixmap(resource_path('./images/pen.png'))

        self.editButton = None
        if self.itemContent.contentType in editable_types:
            self.editButton = EditButton(self)
            self.editButton.pressed.connect(self.changeValue)
            self.editButton.setPos(self.imageCenter)

        self.toolsTipSetted = False
        self.break_flag = False

    def computeGeometry(self):
        center = QPointF(0, 0)
        self.inputTopLeft = center - QPointF(self.InputWidth / 2.0, self.InputHeight / 2.0)
        self.titleTopLeft = self.inputTopLeft + QPointF(self.InputWidth + self.MarginLeft, 0)
        self.imageTopLeft = self.titleTopLeft + QPointF(self.TitleWidth + self.MarginLeft, 0)
        self.inputRect = QRectF(self.inputTopLeft,
                                QSizeF(self.InputWidth, self.InputHeight))
        self.titleRect = QRectF(self.titleTopLeft,
                                QSizeF(self.TitleWidth, self.TitleHeight))
        self.imageCenter = self.imageTopLeft + QPointF(self.ImageWidth / 2.0,
                                                       self.ImageHeight / 2.0)
        self.imageRect = QRectF(self.imageTopLeft,
                                QSizeF(self.ImageWidth, self.ImageHeight))

        self.innerInputRect = QRectF(self.inputTopLeft / 2,
                                     self.inputRect.size() / 2)

    def boundingRect(self):
        totalWidth = self.InputWidth + self.TitleWidth + 2 * self.MarginLeft + self.ImageWidth
        return QRectF(self.inputTopLeft,
                      QSizeF(totalWidth, self.InputHeight))

    def center(self):
        return QPointF(0, 0)

    def polygon(self):
        return QPolygonF([
            self.inputRect.topLeft(),
            self.inputRect.bottomLeft(),
            self.inputRect.bottomRight(),
            self.inputRect.topRight()])

    def paint(self, painter, option, widget=None):
        if self.itemContent.contentValue is None:
            self.title = self.itemType.typeName
        else:
            self.title = '%s: %s' % (self.itemType.typeName,
                                     self.itemContent.contentValue)

        painter.setRenderHint(QPainter.Antialiasing, True)

        lineColor = self.itemContentColor

        penWidth = 2
        pen = QPen()
        pen.setColor(lineColor)
        pen.setWidth(penWidth)
        pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(pen)
        # 当有链接之后，将不再有填充颜色
        if len(self.arrows) == 0:
            painter.setBrush(self.itemContentColor)
        painter.drawEllipse(self.innerInputRect)
        # painter.drawEllipse(self.inputRect)

        penWidth = 1
        pen.setWidth(penWidth)

        if self.itemContent.isEdited or len(self.arrows) != 0:
            # pen.setColor(Qt.gray)
            if self.itemContent.contentType == 'Event':
                # Event类型，文字为白色
                pen.setColor(Qt.white)
            else:
                # 其他类型，文字均为淡蓝色
                pen.setColor(QColor(109, 155, 162))
            painter.setPen(pen)
            painter.setFont(FontManager().customFont())
            painter.drawText(self.titleRect,
                             Qt.AlignLeft | Qt.AlignVCenter,
                             self.title)
            pen.setColor(lineColor)
            painter.setPen(pen)
        else:
            pen.setColor(Qt.gray)
            painter.setPen(pen)
            painter.setFont(FontManager().customFont())
            painter.drawText(self.titleRect,
                             Qt.AlignLeft | Qt.AlignVCenter,
                             self.title)

    # painter.drawRect(self.inputRect)

    # if self.itemContent.contentType in editable_types:
    #     painter.drawPixmap(self.imageRect,
    #         self.pixmap,
    #         self.imageSourceRect)

    def contextMenuEvent(self, event):
        if self.itemContent.contentType != 'Event':
            return
        self.menu = QMenu()
        breakPointAction = self.menu.addAction('BreakPoint')
        # triggerAction = menu.addAction('Trigger')
        breakPointAction.triggered.connect(self.breakPointAct)
        # triggerAction.triggered.connect(self.triggerNodeEvent)
        self.menu.exec_(event.screenPos())
        super().contextMenuEvent(event)

    def breakPointAct(self):
        if not self.break_flag:
            self.break_point = BreakPoint(self)
            self.break_point.pressed.connect(self.delBreakPoint)
            self.break_point.setPos(self.imageCenter)
            self.break_flag = True
            self.parentItem().hasBreakPoint = True

    def delBreakPoint(self):
        self.break_point.deleteLater()
        self.break_flag = False
        self.parentItem().hasBreakPoint = False
        self.update()

    def triggerNodeEvent(self):
        if not self.scene().isRun:
            return
        argId = self.itemType.typeId
        node_uuid = self.parentItem().uuid
        node_idx = self.scene().uuididxmap[node_uuid]
        parentDataArgs = self.parentItem().data['args']
        for arg in parentDataArgs:
            if arg['name'][1] == argId:
                funcId = arg['function']
                break
        from RPyCClient import RpycController
        r = RpycController()
        r.connect()
        G = r.Base.GlobalRef.GlobalRef

    def mousePressEvent(self, event):
        self.parentItem().setSelected(True)
        super(DiagramItemInput, self).mousePressEvent(event)

    # def mouseMoveEvent(self, event):
    # 	self.parentItem().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.parentItem().setSelected(True)
        super(DiagramItemInput, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(self.__class__, self).mouseDoubleClickEvent(event)
        if self.parentItem().mode != 'normal':
            print('pop comment template dialog', self.title)
            self.editTemplate()
        else:
            if not self.itemContent.contentType in editable_types:
                return

            # 已经连线，不能再填值
            if len(self.arrows) != 0:
                return

            self.changeValue()

    def hoverEnterEvent(self, event):
        if self.parentItem().mode != 'normal' and not self.toolsTipSetted:
            tipText = self.scene().getNoteText(self.itemType.typeId)
            if tipText != '':
                self.setToolTip(
                    tipText
                )
                self.toolsTipSetted = True

    def hoverLeaveEvent(self, event):
        pass

    def hoverMoveEvent(self, event):
        pass

    def doneChangeContentValue(self, value, mode='set'):
        if mode == 'set':
            # 将 itemContent的值设置为给定的值
            print('done changed to', value)
            self.itemContent.contentValue = value
            newTitleText = self.itemType.typeName + ': ' + str(value)
            self.setTitle(newTitleText)
            self.itemContent.isEdited = True
            self.scene().editSignal.emit()

            maxWidth = measureWidth(self.itemType.typeName + ': ')
            while maxWidth > self.TitleWidth:
                self.parentItem().wider()
        elif mode == 'reset':
            # 将 itemContent的值 设置为原有的默认值
            print('reset to default')
            self.itemContent.contentValue = self.itemContent.defaultValue
            self.itemContent.isEdited = False
            self.scene().editSignal.emit()
            self.update()
        elif mode == 'del':
            # 删除目前赋予的itemContent的值，即改为None
            print('delete value')
            self.itemContent.contentValue = None
            self.itemContent.isEdited = True
            self.scene().editSignal.emit()
            self.update()

    def changeValue(self):
        dialog = ChangeValueDialog(self.itemType.typeName,
                                   self.itemContent.contentType,
                                   self.itemContent.contentValue,
                                   self.doneChangeContentValue)
        if dialog.exec_():
            print('accept')
        else:
            print('reject')

    def editTemplate(self):
        dialog = TemplateDialog(self.itemType.typeName,
                                self.scene().getNote(self.itemType.typeId),
                                self.doneEditTemplate)
        if dialog.exec_():
            print('accept template')
        else:
            print('reject template')

    def doneEditTemplate(self, note):
        self.scene().updateItemTextNote(self.itemType.typeId, note)

    def hasConnect(self, startItem):
        for arrow in self.arrows:
            start = arrow.startItem()
            if start.parentItem() == startItem.parentItem() \
                    and start.itemType.typeId == startItem.itemType.typeId:
                return True

        return False

    def wider(self):
        self.TitleWidth += 20
        self.computeGeometry()
        if self.editButton is not None:
            self.editButton.setPos(self.imageCenter)
        self.update()

    def thinner(self):
        if self.TitleWidth <= 120:
            return

        self.TitleWidth -= 20
        self.computeGeometry()
        if self.editButton is not None:
            self.editButton.setPos(self.imageCenter)
        self.update()


class DiagramItemOutput(DiagramItemBase):
    OutputWidth, OutputHeight = 20, 20
    TitleWidth, TitleHeight = 130, 20
    MarginRight = 5
    MarginTop = 10

    def __init__(self, parent=None, scene=None, itemType=None, itemContent=None, deltaWidth=0):
        super(DiagramItemOutput, self).__init__(parent, scene, itemType, itemContent)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setAcceptHoverEvents(True)

        self.TitleWidth += deltaWidth

        self.computeGeometry()

        self.itemContent = itemContent

        self.itemContentColor = ColorManager().getColor('data',
                                                        itemContent.contentType)

        self.toolsTipSetted = False

    def computeGeometry(self):
        center = QPointF(0, 0)
        self.outputTopLeft = center - QPointF(self.OutputWidth / 2.0, self.OutputHeight / 2.0)
        self.titleTopLeft = self.outputTopLeft - QPointF(self.MarginRight + self.TitleWidth, 0)

        self.outputRect = QRectF(self.outputTopLeft,
                                 QSizeF(self.OutputWidth, self.OutputHeight))
        self.titleRect = QRectF(self.titleTopLeft,
                                QSizeF(self.TitleWidth, self.TitleHeight))

        self.innerOutputRect = QRectF(self.outputTopLeft / 2,
                                      self.outputRect.size() / 2)

    def boundingRect(self):
        return QRectF(self.titleTopLeft,
                      QSizeF(self.TitleWidth + self.MarginRight + self.OutputWidth,
                             self.OutputHeight))

    def center(self):
        return QPointF(0, 0)

    def polygon(self):
        return QPolygonF([
            self.outputRect.topLeft(),
            self.outputRect.bottomLeft(),
            self.outputRect.bottomRight(),
            self.outputRect.topRight()])

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)

        lineColor = self.itemContentColor

        penWidth = 2
        pen = QPen()
        pen.setColor(lineColor)
        pen.setWidth(penWidth)
        pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(pen)
        if len(self.arrows) == 0:
            painter.setBrush(self.itemContentColor)
        painter.drawEllipse(self.innerOutputRect)
        # painter.drawEllipse(self.outputRect)

        # painter.drawRect(self.titleRect)
        penWidth = 1
        pen.setWidth(penWidth)

        if len(self.arrows) == 0:
            # 没有连接
            pen.setColor(Qt.gray)
            painter.setPen(pen)
            painter.setFont(FontManager().customFont())
            painter.drawText(self.titleRect,
                             Qt.AlignRight | Qt.AlignVCenter, self.title)
        else:
            # 已有连接
            if self.itemContent.contentType == 'Event':
                # Event类型，文字为白色
                pen.setColor(Qt.white)
            else:
                # 其他类型，均为淡蓝色
                pen.setColor(QColor(109, 155, 162))
            painter.setPen(pen)
            painter.setFont(FontManager().customFont())
            painter.drawText(self.titleRect,
                             Qt.AlignRight | Qt.AlignVCenter, self.title)

    # painter.drawRect(self.outputRect)

    def contextMenuEvent(self, event):
        if self.itemContent.contentType != 'Event':
            return
        menu = QMenu()
        triggerAction = menu.addAction('Trigger')
        triggerAction.triggered.connect(self.triggerNodeEvent)
        menu.exec_(event.screenPos())

    def triggerNodeEvent(self):
        if not self.scene().isRun:
            return
        eventName = self.itemType.typeName
        node_uuid = self.parentItem().uuid
        node_idx = self.scene().uuididxmap[node_uuid]
        from RPyCClient import RpycController
        r = RpycController()
        r.connect()
        G = r.Base.GlobalRef.GlobalRef

    def mouseDoubleClickEvent(self, event):
        if self.parentItem().mode != 'normal':
            print('pop comment item dialog', self.title)
            self.editTemplate()
        super(DiagramItemOutput, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        self.parentItem().setSelected(True)
        super(DiagramItemOutput, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(DiagramItemOutput, self).mouseReleaseEvent(event)

    def hoverEnterEvent(self, event):
        if self.parentItem().mode != 'normal' and not self.toolsTipSetted:
            tipText = self.scene().getNoteText(self.itemType.typeId)
            if tipText != '':
                self.setToolTip(
                    tipText
                )
                self.toolsTipSetted = True

    def hoverLeaveEvent(self, event):
        pass

    def hoverMoveEvent(self, event):
        pass

    def hasConnect(self, endItem):
        for arrow in self.arrows:
            end = arrow.endItem()
            if end.parentItem().uuid == endItem.parentItem().uuid \
                    and end.itemType.typeId == endItem.itemType.typeId:
                return True

        return False

    def wider(self):
        self.TitleWidth += 20
        self.computeGeometry()
        self.update()

    def thinner(self):
        if self.TitleWidth <= 120:
            return
        self.TitleWidth -= 20
        self.computeGeometry()
        self.update()

    def editTemplate(self):
        dialog = TemplateDialog(self.itemType.typeName,
                                self.scene().getNote(self.itemType.typeId),
                                self.doneEditTemplate)
        if dialog.exec_():
            print('accept template')
        else:
            print('reject template')

    def doneEditTemplate(self, note):
        self.scene().updateItemTextNote(self.itemType.typeId, note)


class DiagramItemUnfold(QGraphicsItem):
    Width, Height = 180, 20

    def __init__(self, parent=None, deltaWidth=0):
        super(DiagramItemUnfold, self).__init__(parent)

        self.Width += deltaWidth

        self.backgroundColor = ColorManager().getColor('body', 'unfold')
        self.computeGeometry()
        self.initSubItems()

    def computeGeometry(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        center = QPointF(0, 0)
        self.topLeft = center - QPointF(self.Width / 2.0, self.Height / 2.0)

        self.centerRect = QRectF(self.topLeft, QSizeF(self.Width, self.Height))

    def initSubItems(self):
        center = QPointF(0, 0)

        unfoldButton = UnfoldButton(parent=self)
        unfoldButton.setPos(center)
        unfoldButton.pressed.connect(self.unfoldParent)

    def center(self):
        return QPointF(0, 0)

    def boundingRect(self):
        return QRectF(self.topLeft,
                      QSizeF(self.Width, self.Height))

    def unfoldParent(self):
        self.parentItem().unfold()

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.backgroundColor)

        painter.drawRect(self.centerRect)

    def wider(self):
        self.Width += 20
        self.computeGeometry()
        self.update()

    def thinner(self):
        if self.Width <= 180:
            return
        self.Width -= 20
        self.computeGeometry()
        self.update()


class CommentItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super(CommentItem, self).__init__(text, parent)
        self.setTextInteractionFlags(Qt.TextEditable)
        self.setDefaultTextColor(Qt.gray)
        self.setFont(FontManager().commentFont())

    def keyPressEvent(self, event):
        super(CommentItem, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        super(CommentItem, self).keyReleaseEvent(event)

    def paint(self, painter, option, widget=None):
        super(CommentItem, self).paint(painter, option, widget)


class FreeCommentItem(QGraphicsTextItem):
    def __init__(self, text, parent=None):
        super(FreeCommentItem, self).__init__(text, parent)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.setTextInteractionFlags(Qt.TextEditable)
        self.setDefaultTextColor(Qt.gray)
        self.setFont(FontManager().freeCommentFont())

    def keyPressEvent(self, event):
        super(FreeCommentItem, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        super(FreeCommentItem, self).keyReleaseEvent(event)

    def paint(self, painter, option, widget=None):
        super(FreeCommentItem, self).paint(painter, option, widget)


class VirtualRect(QGraphicsItem):
    def __init__(self, parent=None, scene=None):
        super(VirtualRect, self).__init__(parent)

    def boundingRect(self):
        return QRectF(-100, -50, 200, 100)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)

        pen = QPen()
        pen.setColor(Qt.gray)
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(-100, -50, 200, 100)


class SelectionRect(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super(SelectionRect, self).__init__(rect, parent)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)

        pen = QPen()
        pen.setColor(Qt.white)
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.rect())


class ErrorRect(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super(ErrorRect, self).__init__(rect, parent)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)

        pen = QPen()
        pen.setColor(Qt.red)
        pen.setWidth(3)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.rect())


class UnfoldButton(QGraphicsWidget):
    pressed = pyqtSignal()

    def __init__(self, parent=None):
        super(UnfoldButton, self).__init__(parent)

        self._pix = QPixmap(resource_path('.images/down.png')).scaled(QSize(14, 14))

        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())

        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)

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
            painter.translate(1, 1)

        painter.drawEllipse(r.adjusted(2, 2, -2, -2))
        painter.drawPixmap(-self._pix.width() / 2, -self._pix.height() / 2,
                           self._pix)

    def mousePressEvent(self, event):
        self.pressed.emit()

    def mouseReleaseEvent(self, event):
        pass


class FoldButton():
    pressed = pyqtSignal()

    def __init__(self, parent=None):
        super(FoldButton, self).__init__(parament=None)

        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.boundingRect())

        return path

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing, True)

        down = option.state & QStyle.State_Sunken
        r = self.boundingRect()

    def mousePressEvent(self, event):
        self.pressed.emit()
        self.update()

    def mouseReleaseEvent(self, event):
        self.update()


class EditButton(QGraphicsWidget):
    pressed = pyqtSignal()

    def __init__(self, parent=None):
        super(EditButton, self).__init__(parent)

        self._pix = QPixmap(resource_path('images/pen.png'))

        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-15, -15, 30, 30)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawPixmap(-self._pix.width() / 2, -self._pix.height() / 2,
                           self._pix)

    def mousePressEvent(self, event):
        # 发射鼠标按压信号
        self.pressed.emit()

    def mouseReleaseEvent(self, event):
        pass

    def hoverMoveEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)


class BreakPoint(QGraphicsWidget):
    pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptHoverEvents(True)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def boundingRect(self):
        return QRectF(-10, -10, 20, 20)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(Qt.red)
        painter.setPen(Qt.NoPen)
        painter.drawRect(QRectF(-5, -5, 10, 10))

    def mousePressEvent(self, event):
        self.pressed.emit()

    def hoverMoveEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
