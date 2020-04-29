# coding:utf-8


# 使用各个item的频率 节点
from functools import cmp_to_key


class ItemFrequencyNode(object):
    def __init__(self, typeName, typeId, count=0):
        self.typeName = typeName
        self.typeId = typeId
        self.count = count

    def __repr__(self):
        return 'id(%s), name(%s), %d' % (self.typeId, self.typeName, self.count)


# 用户行为跟踪
class BehaviorTracker(object):
    def __init__(self):
        self.freq = {}
        self.updated = False

    def cmp(self, x, y):
        if x.count < y.count: return -1
        if x.count == y.count: return 0
        if x.count > y.count: return 1

    def initialize(self, nameInfos):
        if len(self.freq) != 0:
            # 只能初始化一次
            return

        for nameInfo in nameInfos:
            self.freq[nameInfo[-1]] = ItemFrequencyNode(nameInfo[0],
                                                        nameInfo[-1],
                                                        0)

        self.sortedItems = sorted(list(self.freq.values()),
                                  key=cmp_to_key(self.cmp), reverse=True)

    def trackAdd(self, uid):
        if uid in self.freq:
            self.freq[uid].count += 1
            self.updated = True
        else:
            print('not in track', uid)

    def topItems(self, n=3):
        if self.updated:
            self.sortedItems = sorted(list(self.freq.values()),
                                      key=cmp_to_key(self.cmp), reverse=True)

        if n < len(self.sortedItems):
            return self.sortedItems[:n]
        else:
            return self.sortedItems


def test():
    nameInfos = [['AAA', '111'], ['BBB', '222'], ['CCC', '333']]

    tracker = BehaviorTracker()
    tracker.initialize(nameInfos)
    print('0 track')
    for item in tracker.topItems(n=3):
        print(item)
    print('*******')

    tracker.trackAdd('111')
    tracker.trackAdd('111')
    tracker.trackAdd('333')
    print('1 track')
    for item in tracker.topItems(n=3):
        print(item)
    print('*******')


if __name__ == '__main__':
    test()
