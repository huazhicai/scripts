# coding:utf-8
from util import singleton, MenuTree
from btracker import BehaviorTracker
import json
import uuid
from graphics import *
import data
import copy
import sys


@singleton
class ControllerManager(object):
    def __init__(self):
        self.itemData = self.loadItemData()
        self.controllers = {}
        self.menuTree = MenuTree(self.itemData)
        self.checkItemData()
        self.tracker = BehaviorTracker()
        self.initTracker()

    def initTracker(self):
        """
        初始化跟踪
        """
        nameInfos = []
        for data in self.itemData:
            nameInfos.append(tuple(data['name']))
        self.tracker.initialize(nameInfos)

    def addController(self):
        # 生成访问特定 controller的 key
        cKey = str(uuid.uuid1())
        self.controllers[cKey] = Controller(self.itemData)
        return cKey

    def getController(self, cKey):
        c = self.controllers.get(cKey, None)
        return c

    def removeController(self, cKey):
        if cKey in self.controllers:
            del self.controllers[cKey]
            return True
        else:
            return False

    def optionalItemNames(self):
        """获得可用的item的名称列表"""
        names = []
        for item in self.itemData:
            names.append(item['name'])

        return names

    def loadItemData(self):
        """加载右键菜单模板数据"""
        return data.load_nodes_meta_information()

    def checkItemData(self):
        """
        读取所有的UUID并检查是否存在重复
        重复的Id被写入到duplicate_uuid.txt中
        """
        uuidSet = set()
        dupSet = set()

        for node in self.itemData:
            # 检查returns
            returns = node.get('returns', None)
            if returns is not None:
                for ret in returns:
                    retId = ret['name'][-1]
                    if retId in uuidSet:
                        dupSet.add(retId)
                    else:
                        uuidSet.add(retId)

            # 检查args
            args = node.get('args', None)
            if args is not None:
                for arg in args:
                    argId = arg['name'][-1]
                    if argId in uuidSet:
                        dupSet.add(argId)
                    else:
                        uuidSet.add(argId)

            # 检查name
            nm = node.get('name', None)
            assert nm is not None, '%s has node name unseted' % node
            nmId = nm[-1]
            if nmId in uuidSet:
                dupSet.add(nmId)
            else:
                uuidSet.add(nmId)

        # 如果dupSet为非空，说明存在重复的uuid,
        # 将其写入到文件中，并给出弹出框提示
        if len(dupSet) == 0:
            return

        QMessageBox.warning(None,
                            'Warning',
                            '检测到有重复的uuid，请参照duplicate_uuid.txt，将重复的uuid进行修改',
                            QMessageBox.Ok)

        with open('duplicate_uuid.txt', 'w') as f:
            for uId in dupSet:
                f.write('%s\n' % uId)


class Controller(object):
    def __init__(self, itemData):
        self.itemData = itemData
        self.orderedItemData = self.buildOrderedData(itemData)
        self._selectedItemType = itemData[0]['name']
        self.nodes = []
        self.edges = []
        self.comments = []
        self.currentItemDepth = 0

    # 创建 typeId -> name 的关系映射
    # self.typeId2Name = {}
    # for nodeDef in itemData:
    # 	self.typeId2Name[nodeDef['name'][-1]] = self.typeId2Name[nodeDef['name'][0]]
    # 	for argDef in nodeDef['args']:
    # 		self.typeId2Name[argDef['name'][-1]] = self.typeId2Name[argDef['name'][0]]
    # 	for retDef in nodeDef['returns']:
    # 		self.typeId2Name[retDef['name'][-1]] = self.typeId2Name[retDef['name'][0]]

    def buildOrderedData(self, itemData):
        from collections import OrderedDict
        lst = [(iData['name'][-1], iData) for iData in itemData]

        # item-name-id : item-data
        od = OrderedDict(lst)
        return od

    @property
    def selectedItemType(self):
        return self._selectedItemType

    @selectedItemType.setter
    def selectedItemType(self, value):
        self._selectedItemType = value
    # def selectedItemType():
    #     doc = "The selectedItemType property."
    #
    #     def fget(self):
    #         return self._selectedItemType
    #
    #     def fset(self, value):
    #         self._selectedItemType = value
    #
    #     def fdel(self):
    #         del self._selectedItemType
    #
    #     return locals()
    #
    # selectedItemType = property(**selectedItemType())

    def genUUID(self):
        return str(uuid.uuid4())

    def genProperItem(self):
        if self.selectedItemType.typeId in self.orderedItemData:
            item = DiagramItem(data=self.orderedItemData[
                self.selectedItemType.typeId])
            item.setUUID(self.genUUID())
            return item

        return None

    def restoreItemFromData(self, data):
        if 'type' not in data:
            return None

        if data['type'] in self.orderedItemData:
            item = DiagramItem(data=self.orderedItemData[data['type']], depth=self.currentItemDepth)
            self.currentItemDepth += 1
            if 'id' in data:
                item.setUUID(data['id'])
            else:
                item.setUUID(self.genUUID())
            return item

        return None

    def getSelectedData(self):
        if self.selectedItemType.typeId in self.orderedItemData:
            return copy.deepcopy(self.orderedItemData[self.selectedItemType.typeId])
        return None

    def genItemWithData(self, gnodedata):
        for data in self.itemData:
            if data['name'][-1] == gnodedata['type']:
                customData = copy.deepcopy(data)
                if 'deltaWidth' in gnodedata:
                    customData.update({'deltaWidth': gnodedata['deltaWidth']})

                item = DiagramItem(data=customData, depth=self.currentItemDepth)
                self.currentItemDepth += 1
                item.setUUID(str(uuid.UUID(gnodedata['id'])))
                item.updateContentValues(gnodedata['args'])
                return item

        QMessageBox.warning(None,
                            'Warning',
                            '根据图数据生成item出错，图数据和nodes.json元数据定义不一致',
                            QMessageBox.Ok)
        print('cant find ', gnodedata['type'], 'in nodes.json')
        sys.exit(1)

    def addNode(self, item):
        self.nodes.append(item)

    def getBreakPoints(self):
        breakPoints = []
        for node in self.nodes:
            if node.hasBreakPoint == True:
                breakPoints.append(node.uuid)
        return breakPoints

    def removeNode(self, item):
        try:
            self.nodes.remove(item)
        except ValueError as e:
            pass

    def addEdge(self, startItem, endItem,
                startItemType, endItemType, linkType):
        self.edges.append({
            'start': startItem.uuid,
            'startNodeName': startItem.itemType.typeName,
            'end': endItem.uuid,
            'endNodeName': endItem.itemType.typeName,
            'startItemId': startItemType.typeId,
            'startItemName': startItemType.typeName,
            'endItemId': endItemType.typeId,
            'endItemName': endItemType.typeName,
            'linktype': linkType
        })

    def removeEdge(self, startItem, endItem,
                   startItemTypeId, endItemTypeId):
        selectedEdge = None
        for edge in self.edges:
            if edge['start'] == startItem.uuid and \
                    edge['end'] == endItem.uuid and \
                    edge['startItemId'] == startItemTypeId and \
                    edge['endItemId'] == endItemTypeId:
                selectedEdge = edge
                break

        if selectedEdge is not None:
            self.edges.remove(selectedEdge)
        else:
            print('error: no selected edge delete')

    def addFreeComment(self, fComment):
        self.comments.append(fComment)

    def removeFreeComment(self, fComment):
        try:
            self.comments.remove(fComment)
        except ValueError as e:
            pass

    def generateGraphData(self):
        data = {}
        scene_data = {}
        nodes_data = []
        edges_data = []
        comments_data = []

        scene_data['width'] = self.scene.sceneRect().width()
        scene_data['height'] = self.scene.sceneRect().height()

        for node in self.nodes:
            nodes_data.append(self.nodeToData(node))

        for comm in self.comments:
            pos = comm.scenePos()
            comments_data.append({
                'text': str(comm.toPlainText()),
                'pos': {
                    'x': pos.x(),
                    'y': pos.y()
                }
            })

        data['scene'] = scene_data
        data['nodes'] = nodes_data
        data['edges'] = self.edges
        data['comments'] = comments_data
        return data

    def saveGraph(self, filename=''):
        data = self.generateGraphData()
        self.attachMetaToData(data)
        with open('%s' % filename, 'w') as f:
            json.dump(data, f, indent=4)

    def getData(self):
        data = self.generateGraphData()
        self.attachMetaToData(data)
        return data

    def attachMetaToData(self, data):
        """
        给level数据，附加meta信息
        """
        usedNodeKeys = set([node['type'] for node in data['nodes']])

        metas = []
        for nodeDef in self.itemData:
            if nodeDef['name'][-1] in usedNodeKeys:
                metas.append(nodeDef)

        data['meta'] = metas

    def nodeToData(self, item, center=None):
        """
        有center参数时，用于copy/cut/paste的功能，可以定位相对中心点。
        没有center参数时。用于保存整图。
        """
        if center is None:
            # 使用绝对位置
            itemPos = item.scenePos()
        else:
            # 使用相对位置
            pos = item.scenePos()
            itemPos = pos - center

        nodeData = {
            'id': item.uuid,
            'type': item.itemType.typeId,
            'pos': {
                'x': itemPos.x(),
                'y': itemPos.y()
            },
            'deltaWidth': item.deltaWidth
        }

        if item.comment is not None:
            nodeData['comment'] = str(item.comment.toPlainText())

        args = {}
        for subitem in item.childItems():
            if isinstance(subitem, DiagramItemInput) and \
                    subitem.itemContent.contentValue is not None:
                # if subitem.itemType.typeName == 'Vec3':
                if subitem.itemContent.contentType == 'Vec3':
                    args[subitem.itemType.typeId] = str(subitem.itemContent.contentValue)
                else:
                    args[subitem.itemType.typeId] = subitem.itemContent.contentValue
        nodeData['args'] = args

        return nodeData

    def nodeToDataWithEdge(self, item, center=None):
        """
        将node及其附带的边，转化成数据
        """
        if center is None:
            itemPos = item.scenePos()
        else:
            pos = item.scenePos()
            itemPos = pos - center

        nodeData = {
            'id': item.uuid,
            'type': item.itemType.typeId,
            'pos': {
                'x': itemPos.x(),
                'y': itemPos.y()
            },
            'deltaWidth': item.deltaWidth
        }

        if item.comment is not None:
            nodeData['comment'] = str(item.comment.toPlainText())

        inEdgeData = []  # 入边
        outEdgeData = []  # 出边

        args = {}
        for subItem in item.childItems():
            if isinstance(subItem, DiagramItemInput):
                if len(subItem.arrows) == 0:
                    if subItem.itemContent.contentValue is not None:
                        # if subItem.itemType.typeName == 'Vec3':
                        if subItem.itemContent.contentType == 'Vec3':
                            args[subItem.itemType.typeId] = str(subItem.itemContent.contentValue)
                        else:
                            args[subItem.itemType.typeId] = subItem.itemContent.contentValue
                    continue

                # 有入边
                for arrow in subItem.arrows:
                    startItem = arrow.startItem()
                    inEdgeData.append({
                        'start': startItem.parentItem().uuid,
                        'end': subItem.parentItem().uuid,
                        'startItemTypeId': startItem.itemType.typeId,
                        'endItemTypeId': subItem.itemType.typeId
                    })

            elif isinstance(subItem, DiagramItemOutput):
                if len(subItem.arrows) == 0:
                    continue

                # 有出边
                for arrow in subItem.arrows:
                    endItem = arrow.endItem()
                    outEdgeData.append({
                        'start': subItem.parentItem().uuid,
                        'end': endItem.parentItem().uuid,
                        'startItemTypeId': subItem.itemType.typeId,
                        'endItemTypeId': endItem.itemType.typeId
                    })
        nodeData['args'] = args

        return {'node': nodeData,
                'inEdgeData': inEdgeData,
                'outEdgeData': outEdgeData}

    def getPrevNode(self, item):
        prevNodeList = []
        for subItem in item.childItems():
            if isinstance(subItem, DiagramItemInput):
                if len(subItem.arrows) == 0:
                    continue

                # 有前驱
                for arrow in subItem.arrows:
                    startItem = arrow.startItem()
                    prevNodeList.append(startItem.parentItem())
        return prevNodeList

    def getNextNode(self, item):
        nextNodeList = []
        for subItem in item.childItems():
            if isinstance(subItem, DiagramItemOutput):
                if len(subItem.arrows) == 0:
                    continue

                # 有后继
                for arrow in subItem.arrows:
                    endItem = arrow.endItem()
                    nextNodeList.append(endItem.parentItem())
        return nextNodeList

    def getPrevEdge(self, item):
        prevEdgeList = []
        for subItem in item.childItems():
            if isinstance(subItem, DiagramItemInput):
                if len(subItem.arrows) == 0:
                    continue

                # 有前驱
                for arrow in subItem.arrows:
                    prevEdgeList.append(arrow)
        return prevEdgeList

    def getNextEdge(self, item):
        nextEdgeList = []
        for subItem in item.childItems():
            if isinstance(subItem, DiagramItemOutput):
                if len(subItem.arrows) == 0:
                    continue

                # 有后继
                for arrow in subItem.arrows:
                    nextEdgeList.append(arrow)
        return nextEdgeList

    def setScene(self, scene):
        self.scene = scene

    def restoreFromData(self, scene, filename=''):
        while len(self.nodes) > 0:
            self.nodes.pop()
        while len(self.edges) > 0:
            self.edges.pop()

        graph = data.load_graph_information(filename)

        # 检查当前的图数据与节点定义是否兼容
        if not self.compatCheck(graph):
            QMessageBox.warning(None,
                                'Warning',
                                '图文件与nodes.json元文件中的值类型有冲突，请联系程序进行转换',
                                QMessageBox.Ok)
            return False

        # 恢复场景大小
        sceneWidth = graph['scene']['width']
        sceneHeight = graph['scene']['height']
        scene.setSceneRect(QRectF(-sceneWidth / 2.0,
                                  -sceneHeight / 2.0,
                                  sceneWidth,
                                  sceneHeight))

        # 恢复顶点
        node_map = {}
        for gnode in graph['nodes']:
            item = self.genItemWithData(gnode)
            scene.addItem(item)
            scene.addToCache(item)
            self.addNode(item)
            item.setPos(gnode['pos']['x'], gnode['pos']['y'])
            commentText = gnode.get('comment', None)
            if commentText is not None:
                commentItem = CommentItem(commentText)
                scene.addItem(commentItem)
                topLeft = item.polygon()[0] + item.scenePos()
                commentPos = topLeft + QPointF(0, -50)
                commentItem.setPos(commentPos)
                item.setComment(commentItem)

            node_map[item.uuid] = item

        # 恢复边
        for gedge in graph['edges']:
            startNodeId, endNodeId = gedge['start'], gedge['end']
            startItemTypeId, endItemTypeId = gedge['startItemId'], gedge['endItemId']

            startNode = node_map.get(startNodeId, None)
            endNode = node_map.get(endNodeId, None)

            startItem, endItem = None, None
            for subitem in startNode.childItems():
                if subitem.itemType.typeId == startItemTypeId:
                    startItem = subitem

            for subitem in endNode.childItems():
                if subitem.itemType.typeId == endItemTypeId:
                    endItem = subitem

            if startItem is None or endItem is None:
                continue

            arrow = CosineConnection(startItem, endItem)
            if startItem.itemContent.contentType != 'Any':
                arrow.setConnectionType(startItem.itemContent.contentType)
                arrow.setColor(startItem.itemContentColor)
            else:
                arrow.setConnectionType(endItem.itemContent.contentType)
                arrow.setColor(endItem.itemContentColor)

            # self.addEdge(startItem.parentItem(),
            # 	endItem.parentItem(),
            # 	startItem.itemType,
            # 	endItem.itemType,
            # 	startItem.itemContent.contentType)
            self.addEdge(startItem.parentItem(),
                         endItem.parentItem(),
                         startItem.itemType,
                         endItem.itemType,
                         arrow.connectionType)

            startItem.addArrow(arrow)
            endItem.addArrow(arrow)
            arrow.setZValue(-1000.0)
            scene.addItem(arrow)
            arrow.updatePosition()
            endItem.itemContent.contentValue = None
            startItem.update()
            endItem.update()

        # 恢复注释
        gcomments = graph.get('comments', None)
        if gcomments is None:
            return True

        for gcomment in gcomments:
            freec = FreeCommentItem(gcomment['text'])
            scene.addItem(freec)
            freec.setPos(QPointF(gcomment['pos']['x'],
                                 gcomment['pos']['y']))

            self.addFreeComment(freec)

        # 定位为左右item的中心
        scene.views()[0].centerOn(0, 0)
        return True

    def compatCheck(self, graphData):
        """
        利用图数据和节点定义数据做兼容性检查
        """
        import backcompat

        compatErrors = backcompat.checkCompat(self.itemData, graphData)

        if len(compatErrors) != 0:
            # 有兼容性错误，将其写入到文件当中
            with open('compat_error.json', 'w') as f:
                json.dump(compatErrors, f, indent=4)

        return len(compatErrors) == 0

    def findItemsByName(self, content, resultList):
        """
        名称：模糊查找
        """
        for node in self.nodes:
            if node.itemType.typeName.lower().find(content) != -1:
                resultList.add(node)
                continue

            for subItem in node.childItems():
                if subItem.itemType.typeName.lower().find(content) != -1:
                    resultList.add(node)
                    break

    def findItemsByValue(self, content, resultList):
        """
        值：模糊查找
        """
        for node in self.nodes:
            for subItem in node.childItems():
                if str(subItem.itemContent.contentValue).lower().find(content) != -1:
                    resultList.add(node)
                    break

    def findItemsByComment(self, content, resultList):
        for node in self.nodes:
            if node.comment is None:
                continue

            if str(node.comment.toPlainText()).lower().find(content) != -1:
                resultList.add(node)

    def findNodeByArgValue(self, nodeName, argName, value, chosenNodes=None):
        targetNodes = chosenNodes if chosenNodes else self.nodes
        ret = []
        for node in targetNodes:
            # print node
            # print node.itemType.typeName
            if node.itemType.typeName == nodeName:
                for subItem in node.childItems():
                    if subItem.itemType.typeName == argName and subItem.itemContent.contentValue:
                        # print subItem.itemContent.contentValue.__class__, value.__class__
                        # print subItem.itemContent.contentType.__class__
                        if str(value) in str(subItem.itemContent.contentValue):
                            ret.append(node)
                        # print subItem
                        # print subItem.itemType
                        # print subItem.itemContent.contentValue, subItem.itemContent.contentType
                        # break
        return ret

    def invertIndexByName(self):
        nameIndex = {}
        for node in self.nodes:
            nodeName = node.itemType.typeName.lower()
            nameTerms = nodeName.split()
            for term in nameTerms:
                if term not in nameIndex:
                    nameIndex[term] = set()
                nameIndex[term].add(node)
            for subItem in node.childItems():
                subName = subItem.itemType.typeName.lower()
                subNameTerms = subName.split()
                for subterm in subNameTerms:
                    if subterm not in nameIndex:
                        nameIndex[subterm] = set()
                    nameIndex[subterm].add(node)
        return nameIndex

    def invertIndexByValue(self):
        valueIndex = {}
        for node in self.nodes:
            for subItem in node.childItems():
                subValue = str(subItem.itemContent.contentValue).lower()
                valueTerms = subValue.split(',')
                for valueterm in valueTerms:
                    if valueterm not in valueIndex:
                        valueIndex[valueterm] = set()
                    valueIndex[valueterm].add(node)
        return valueIndex

    def invertIndexByComment(self):
        commentIndex = {}
        for node in self.nodes:
            if node.comment is None:
                continue
            nodeComment = str(node.comment.toPlainText()).lower()
            commentTerms = nodeComment.split()
            for term in commentTerms:
                if term not in commentIndex:
                    commentIndex[term] = set()
                commentIndex[term].add(node)
        return commentIndex
