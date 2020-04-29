# coding:utf-8
from PyQt5.QtCore import QPointF, QPoint
from PyQt5.QtWidgets import QUndoCommand

from controller import ControllerManager
import inspect
import random


def __line__():
    caller = inspect.stack()[-1]
    return int(caller[2])


class CommandAdd(QUndoCommand):
    """
    增加item时，使用的命令
    支持增加一个或多个item；也支持item附带的连接边
    """

    def __init__(self, scene, data, description='', mousePosition=None):
        """
        data的格式
        """
        super(CommandAdd, self).__init__(description)

        self.controllerKey = scene.controllerKey
        self.scene = scene
        self.data = data
        self.isFirst = True
        self.mousePosition = mousePosition

    def randomOffset(self):
        return QPointF(random.randint(30, 80), random.randint(30, 80))

    def redo(self):
        controller = ControllerManager().getController(self.controllerKey)
        if type(self.data) == dict:
            # 从空模板插入一个项目
            item = controller.restoreItemFromData(self.data)
            controller.addNode(item)
            self.scene.addItem(item)
            item.setPos(QPointF(self.data['pos']['x'],
                                self.data['pos']['y']))
            self.data.update({
                'id': '%s' % item.uuid
            })

            self.scene.addToCache(item)
        elif type(self.data) == list:
            # 来自copy/paste
            if self.isFirst:
                # isFirst标识是否是第一次执行redo
                # 如果是第一次，就是一个粘贴操作，各个item的x,y就是一种相对坐标
                # 如果不是第一次，就是执行了undo之后，又执行redo；这时item的x,y就是绝对坐标了。
                if self.mousePosition:
                    vsCenterF = QPointF(self.mousePosition[0], self.mousePosition[1])
                else:
                    view = self.scene.views()[0]
                    size = view.size()
                    width, height = size.width(), size.height()
                    viewCenter = QPoint(width / 2, height / 2)
                    # 可见中心点映射到场景中的位置
                    vsCenter = view.mapToScene(viewCenter)
                    vsCenterF = QPointF(vsCenter.x(), vsCenter.y())
                vsCenterF = vsCenterF + self.randomOffset()

            for itemData in self.data:
                item = controller.genItemWithData(itemData['node'])

                if self.isFirst:
                    relpos = QPointF(itemData['node']['pos']['x'],
                                     itemData['node']['pos']['y'])
                    pos = relpos + vsCenterF
                else:
                    pos = QPointF(itemData['node']['pos']['x'],
                                  itemData['node']['pos']['y'])

                self.scene.addItem(item)
                item.setPos(pos)
                item.setSelected(True)
                controller.addNode(item)

                self.scene.addToCache(item)
                ControllerManager().tracker.trackAdd(item.itemType.typeId)

            # 智能恢复边
            for itemData in self.data:
                inEdgesData = itemData['inEdgeData']
                outEdgesData = itemData['outEdgeData']

                # 恢复入边
                for edgeData in inEdgesData:
                    startParent = self.scene.cache.get(edgeData['start'], None)
                    if startParent is None:
                        # 可插入debug信息
                        continue

                    endParent = self.scene.cache.get(edgeData['end'], None)
                    startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                    endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                    if startItem is None or endItem is None:
                        continue

                    # 建立边
                    self.scene.simpleMakeConnection(startItem, endItem)

                # 恢复出边
                for edgeData in outEdgesData:
                    endParent = self.scene.cache.get(edgeData['end'], None)
                    if endParent is None:
                        continue

                    startParent = self.scene.cache.get(edgeData['start'], None)
                    startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                    endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                    if startItem is None or endItem is None:
                        continue

                    # 建立边
                    self.scene.simpleMakeConnection(startItem, endItem)
        else:
            print('Error: data type must be dict or list', type(self.data), 'given in', __file__, 'line:', __line__())

        self.isFirst = False

    def undo(self):
        controller = ControllerManager().getController(self.controllerKey)
        if type(self.data) == dict:
            # 删除从模板插入的空项目
            item = self.scene.cache[self.data['id']]
            controller.removeNode(item)
            self.scene.removeItem(item)

            self.scene.removeFromCache(item)
        elif type(self.data) == list:
            # 删除copy/paste插入的一个或多个节点

            # 先删除边
            for itemData in self.data:
                inEdgesData = itemData['inEdgeData']
                outEdgesData = itemData['outEdgeData']

                # 删除入边
                for edgeData in inEdgesData:
                    startParent = self.scene.cache.get(edgeData['start'], None)
                    if startParent is None:
                        continue

                    endParent = self.scene.cache.get(edgeData['end'], None)
                    startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                    endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                    if startItem is None or endItem is None:
                        continue

                    for arrow in endItem.arrows[:]:
                        if arrow.startItem().parentItem().uuid == edgeData['start'] and \
                                arrow.startItem().itemType.typeId == startItem.itemType.typeId:
                            self.scene.simpleDisconnection(arrow)
                            break

                # 删除出边
                for edgeData in outEdgesData:
                    endParent = self.scene.cache.get(edgeData['end'], None)
                    if endParent is None:
                        continue

                    startParent = self.scene.cache.get(edgeData['start'], None)
                    startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                    endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                    if startItem is None or endItem is None:
                        continue

                    for arrow in startItem.arrows[:]:
                        if arrow.endItem().parentItem().uuid == edgeData['end'] and \
                                arrow.endItem().itemType.typeId == endItem.itemType.typeId:
                            self.scene.simpleDisconnection(arrow)
                            break

                # 删除节点
                iD = itemData['node']['id']
                item = self.scene.cache.get(iD, None)
                if item is None:
                    continue

                controller.removeNode(item)
                self.scene.removeItem(item)
                self.scene.removeFromCache(item)
        else:
            print('Error: data type must be dict or list', type(self.data), 'given in', __file__, 'line:', __line__())


class CommandDelete(QUndoCommand):
    """
    删除item时，使用的命令
    支持删除一个或多个item；也支持item附带的连接边
    """

    def __init__(self, scene, data, description=''):
        super(CommandDelete, self).__init__(description)

        self.controllerKey = scene.controllerKey
        self.scene = scene
        self.data = data

    def redo(self):
        controller = ControllerManager().getController(self.controllerKey)
        for itemData in self.data:
            # 先删除边
            inEdgesData = itemData['inEdgeData']
            outEdgesData = itemData['outEdgeData']

            # 删除入边
            for edgeData in inEdgesData:
                startParent = self.scene.cache.get(edgeData['start'], None)
                if startParent is None:
                    continue

                endParent = self.scene.cache.get(edgeData['end'], None)
                startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                if startItem is None or endItem is None:
                    continue

                for arrow in endItem.arrows[:]:
                    if arrow.startItem().parentItem().uuid == edgeData['start'] and \
                            arrow.startItem().itemType.typeId == startItem.itemType.typeId:
                        self.scene.simpleDisconnection(arrow)
                        break

            # 删除出边
            for edgeData in outEdgesData:
                endParent = self.scene.cache.get(edgeData['end'], None)
                if endParent is None:
                    continue

                startParent = self.scene.cache.get(edgeData['start'], None)
                startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                if startItem is None or endItem is None:
                    continue

                for arrow in startItem.arrows[:]:
                    if arrow.endItem().parentItem().uuid == edgeData['end'] and \
                            arrow.endItem().itemType.typeId == endItem.itemType.typeId:
                        self.scene.simpleDisconnection(arrow)
                        break

            # 删除节点
            iD = itemData['node']['id']
            item = self.scene.cache.get(iD, None)
            if item is None:
                continue

            controller.removeNode(item)
            self.scene.removeItem(item)
            self.scene.removeFromCache(item)

    def undo(self):
        controller = ControllerManager().getController(self.controllerKey)
        for itemData in self.data:
            item = controller.genItemWithData(itemData['node'])

            pos = QPointF(itemData['node']['pos']['x'], itemData['node']['pos']['y'])
            self.scene.addItem(item)
            item.setPos(pos)
            item.setSelected(True)
            controller.addNode(item)

            self.scene.addToCache(item)

        # 智能恢复边
        for itemData in self.data:
            inEdgesData = itemData['inEdgeData']
            outEdgesData = itemData['outEdgeData']

            # 恢复入边
            for edgeData in inEdgesData:
                startParent = self.scene.cache.get(edgeData['start'], None)
                if startParent is None:
                    # 可插入debug信息
                    continue

                endParent = self.scene.cache.get(edgeData['end'], None)
                startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                if startItem is None or endItem is None:
                    continue

                # 建立边
                self.scene.simpleMakeConnection(startItem, endItem)

            # 恢复出边
            for edgeData in outEdgesData:
                endParent = self.scene.cache.get(edgeData['end'], None)
                if endParent is None:
                    continue

                startParent = self.scene.cache.get(edgeData['start'], None)
                startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
                endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
                if startItem is None or endItem is None:
                    continue

                # 建立边
                self.scene.simpleMakeConnection(startItem, endItem)


class CommandLink(QUndoCommand):
    """
    建立连接时，使用的命令
    支持建立一条或多条连接
    """

    def __init__(self, scene, data, description=''):
        super(CommandLink, self).__init__(description)
        self.controllerKey = scene.controllerKey
        self.scene = scene
        self.data = data

    def redo(self):
        controller = ControllerManager().getController(self.controllerKey)
        for edgeData in self.data:
            startParent = self.scene.cache.get(edgeData['start'], None)
            endParent = self.scene.cache.get(edgeData['end'], None)
            startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
            endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
            if startItem is None or endItem is None:
                continue

            self.scene.directConnection(startItem, endItem)

    def undo(self):
        controller = ControllerManager().getController(self.controllerKey)
        for edgeData in self.data:
            startParent = self.scene.cache.get(edgeData['start'], None)
            endParent = self.scene.cache.get(edgeData['end'], None)
            startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
            endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
            if startItem is None or endItem is None:
                continue

            for arrow in startItem.arrows[:]:
                if arrow.endItem().parentItem().uuid == edgeData['end'] and \
                        arrow.endItem().itemType.typeId == endItem.itemType.typeId:
                    self.scene.simpleDisconnection(arrow)
                    break


class CommandUnLink(QUndoCommand):
    """
    删除连接时，使用的命令
    支持删除一条或多条连接
    """

    def __init__(self, scene, data, description=''):
        super(CommandUnLink, self).__init__(description)
        self.controllerKey = scene.controllerKey
        self.scene = scene
        self.data = data

    def redo(self):
        controller = ControllerManager().getController(self.controllerKey)
        for edgeData in self.data:
            startParent = self.scene.cache.get(edgeData['start'], None)
            endParent = self.scene.cache.get(edgeData['end'], None)

            startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
            endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])

            if startItem is None or endItem is None:
                continue

            for arrow in startItem.arrows[:]:
                if arrow.endItem().parentItem().uuid == edgeData['end'] and \
                        arrow.endItem().itemType.typeId == endItem.itemType.typeId:
                    self.scene.simpleDisconnection(arrow)

    def undo(self):
        controller = ControllerManager().getController(self.controllerKey)
        for edgeData in self.data:
            startParent = self.scene.cache.get(edgeData['start'], None)
            endParent = self.scene.cache.get(edgeData['end'], None)
            startItem = self.scene.findSubItem(startParent, edgeData['startItemTypeId'])
            endItem = self.scene.findSubItem(endParent, edgeData['endItemTypeId'])
            if startItem is None or endItem is None:
                continue

            self.scene.directConnection(startItem, endItem)


class CommandPosition(QUndoCommand):
    """
    移动位置的命令
    支持一个或多个item的移动
    """

    def __init__(self, scene, data, description=''):
        super(CommandPosition, self).__init__(description)
        self.controllerKey = scene.controllerKey
        self.scene = scene
        self.data = data

    def redo(self):
        pass

    def undo(self):
        pass
