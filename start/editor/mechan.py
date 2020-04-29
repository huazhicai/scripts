# coding:utf-8
from graphics import DiagramItemInput, DiagramItemOutput

mechanism = None


class ConnectMechanism(object):
    """
    定义连线的一些限制性条件
    """

    def __init__(self):
        pass

    def sdTypeCheck(self, startItem, endItem):
        """
        检查source, dest的连接类型
        source 必须是Output类型
        dest 必须是Input类型
        """
        return type(startItem) == DiagramItemOutput \
               and type(endItem) == DiagramItemInput \
               and startItem.parentItem() != endItem.parentItem()

    def contentTypeCheck(self, startItem, endItem, restrictValueTypes=None):
        """
        对source, dest的内容类型的检查
        必须具有相同的数据类型
        或者，dest为Any类型，start为除Event之外的其他类型
        """
        if endItem.itemContent.contentType == 'Any':
            return startItem.itemContent.contentType != 'Event'
        elif startItem.itemContent.contentType == 'Any':
            if restrictValueTypes is None:
                return endItem.itemContent.contentType != 'Event'
            else:
                return endItem.itemContent.contentType in restrictValueTypes
        else:
            return startItem.itemContent.contentType == endItem.itemContent.contentType

    def noDuplicateLinkCheck(self, startItem, endItem):
        """
        不可以有重复的连接
        """
        return not startItem.hasConnect(endItem)

    def canConnect(self, startItem, endItem, restrictValueTypes=None):
        return self.sdTypeCheck(startItem, endItem) and \
               self.contentTypeCheck(startItem, endItem, restrictValueTypes) and \
               self.noDuplicateLinkCheck(startItem, endItem)


if mechanism is None:
    mechanism = ConnectMechanism()
