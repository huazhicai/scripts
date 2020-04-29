# coding:utf-8

import math
import numpy as np
import json
from collections import OrderedDict

editable_types = ['Int', 'Float', 'Bool', 'String', 'Vec3', 'Any', 'Dict', 'List']


# 起始点和终止点之间的半条余弦线插值
# 返回一个 len x 2的矩阵，第一列为x轴数值，第二列为y轴数值
# 此插值可以直接被QPainterPath使用
def interpolate_cosine_points(startX, startY, endX, endY, pointStep=20):
    assert pointStep > 0
    if math.fabs(startX - endX) < pointStep * 2 or math.fabs(startY - endY) < pointStep * 2:
        # 处于同一水平或垂直的直线上时，不需要插值操作
        arr = np.zeros((2, 2))
        arr[0, 0] = startX
        arr[0, 1] = startY
        arr[1, 0] = endX
        arr[1, 1] = endY
        return arr

    dx = float(endX - startX)
    dy = float(endY - startY)
    if dx * dy > 0:
        # x = np.arange(startX, endX, np.sign(dx)*pointStep)
        x = np.linspace(startX, endX, num=int(math.fabs(dx) / pointStep), endpoint=True)
        y = startY + dy / 2 * (1 - np.cos(math.pi / dx * (x - startX)))
        arr = np.zeros((len(x), 2))
        arr[:, 0] = x
        arr[:, 1] = y
        return arr
    else:
        # x = np.arange(startX, endX, np.sign(dx)*pointStep)
        x = np.linspace(startX, endX, num=int(math.fabs(dx) / pointStep), endpoint=True)
        y = startY + dy / 2 * (1 + np.sin(math.pi / dx * (x - startX) - math.pi / 2))
        arr = np.zeros((len(x), 2))
        arr[:, 0] = x
        arr[:, 1] = y
        return arr


def singleton(cls):
    instances = {}

    def get_instance(*args, **kargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kargs)
        return instances[cls]

    return get_instance


class Vec3(object):
    def __init__(self, x, y, z):
        self._x = x
        self._y = y
        self._z = z

    def x():
        doc = "The x property."

        def fget(self):
            return self._x

        def fset(self, value):
            self._x = value

        return locals()

    x = property(**x())

    def y():
        doc = "The y property."

        def fget(self):
            return self._y

        def fset(self, value):
            self._y = value

        return locals()

    y = property(**y())

    def z():
        doc = "The z property."

        def fget(self):
            return self._z

        def fset(self, value):
            self._z = value

        return locals()

    z = property(**z())

    def __repr__(self):
        return 'Vec3(%.2f,%.2f,%.2f)' % (self.x, self.y, self.z)

    @classmethod
    def valueFromString(cls, string):
        lpos, rpos = string.find('('), string.rfind(')')
        string = string[lpos + 1:rpos]

        ws = string.split(',')
        if len(ws) == 3:
            try:
                x = float(ws[0])
                y = float(ws[1])
                z = float(ws[2])

                return Vec3(x, y, z)
            except:
                return None
        else:
            return None


def parseValue(contentType, text):
    value = None
    sig = False

    if contentType == 'Int':
        try:
            value = int(text)
            sig = True
        except:
            value = None
    elif contentType == 'Float':
        try:
            value = float(text)
            sig = True
        except:
            value = None
    elif contentType == 'String':
        value = text
        sig = True
    elif contentType == 'Dict':
        try:
            value = eval(text)
        except:
            value = None
        if isinstance(value, dict):
            sig = True
    elif contentType == 'List':
        try:
            value = eval(text)
        except:
            value = None
        if isinstance(value, list):
            sig = True
    elif contentType == 'Bool':
        print('branch bool')
        try:
            value = eval(text.capitalize())
            sig = True
        except:
            value = None
    elif contentType == 'Vec3':
        if (text.startswith('Vec3(') or text.startswith('vec3')) and \
                text.endswith(')'):
            text = text.capitalize()
        else:
            text = 'Vec3(' + text + ')'
        value = Vec3.valueFromString(text)
        sig = False if value is None else True
    elif contentType == 'Any':
        try:
            value = eval(text)
        except NameError:
            value = text
        sig = True

    return sig, value


class ItemType(object):
    def __init__(self, type_name, type_id):
        self._typeName = type_name
        self._typeId = type_id

    @property
    def typeName(self):
        return self._typeName

    @typeName.setter
    def typeName(self, value):
        self._typeName = value

    @property
    def typeId(self):
        return self._typeId

    @typeId.setter
    def typeId(self, value):
        self._typeId = value

    def __repr__(self):
        return 'name:%s,id:%s' % (self.typeName, self.typeId)


# class ItemType(object):
#     def __init__(self, type_name, type_id):
#         self.typeName = type_name
#         self.typeId = type_id
#
#     def typeName():
#         doc = "The typeName property."
#
#         def fget(self):
#             return self._typeName
#
#         def fset(self, value):
#             self._typeName = value
#
#         return locals()
#
#     typeName = property(**typeName())
#
#     def typeId():
#         doc = "The typeId property."
#
#         def fget(self):
#             return self._typeId
#
#         def fset(self, value):
#             self._typeId = value
#
#         return locals()
#
#     typeId = property(**typeId())
#
#     def __repr__(self):
#         return 'name:%s,id:%s' % (self.typeName, self.typeId)


class ItemContent(object):
    def __init__(self, contentType, contentValue):
        self._contentType = contentType
        self._contentValue = contentValue
        self.defaultValue = contentValue
        self._isEdited = False

    @property
    def contentType(self):
        return self._contentType

    @contentType.setter
    def contentType(self, value):
        self._contentType = value

    @property
    def contentValue(self):
        return self._contentValue

    @contentValue.setter
    def contentValue(self, value):
        self._contentValue = value

    @property
    def isEdited(self):
        return self._isEdited

    @isEdited.setter
    def isEdited(self, value):
        self._isEdited = value

    def __repr__(self):
        return 'cname:%s,cval:%s' % (self.contentType,
                                     str(self.contentType))


# class ItemContent(object):
#     def __init__(self, contentType, contentValue):
#         self.contentType = contentType
#         self.contentValue = contentValue
#         self.defaultValue = contentValue
#         self.isEdited = False
#
#     def contentType():
#         doc = "The contentType property."
#
#         def fget(self):
#             return self._contentType
#
#         def fset(self, value):
#             self._contentType = value
#
#         return locals()
#
#     contentType = property(**contentType())
#
#     def contentValue():
#         doc = "The contentValue property."
#
#         def fget(self):
#             return self._contentValue
#
#         def fset(self, value):
#             self._contentValue = value
#
#         return locals()
#
#     contentValue = property(**contentValue())
#
#     def isEdited():
#         doc = "The isEdited property."
#
#         def fget(self):
#             return self._isEdited
#
#         def fset(self, value):
#             self._isEdited = value
#
#         return locals()
#
#     isEdited = property(**isEdited())
#
#     def __repr__(self):
#         return 'cname:%s,cval:%s' % (self.contentType,
#                                      str(self.contentType))


class MenuTree(object):
    def __init__(self, meta_data):
        self.tree = self.buildTree(meta_data)

    def buildTree(self, data):
        tree = OrderedDict()
        for item in data:
            raw_category = item['category']
            name = item['name']
            if '/' in raw_category:
                category = raw_category.split('/')
            else:
                category = raw_category
            if type(category) == list:
                p = tree
                for subcate in category:
                    if subcate not in p:
                        p[subcate] = OrderedDict()
                    p = p[subcate]
                p[name[-1]] = (name[0],)
            else:
                if category not in tree:
                    tree[category] = OrderedDict()
                tree[category][name[-1]] = (name[0],)

        return tree

    def printTree(self):
        print(json.dumps(self.tree, indent=4))
