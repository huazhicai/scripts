# coding:utf-8
import json
from collections import OrderedDict


class MenuTree(object):
    def __init__(self, meta_data):
        self.tree = self.buildTree(meta_data)

    def buildTree(self, data):
        tree = OrderedDict()   # 有序字典
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
                p[name[-1]] = name[0]
            else:
                if category not in tree:
                    tree[category] = OrderedDict()
                tree[category][name[-1]] = name[0]

        return tree

    def printTree(self):
        print(json.dumps(self.tree, indent=4))


def test():
    entities = [
        {
            "category": "B",
            "name": ["Bill", "222"]
        },
        {
            "category": "A/AA",
            "name": ["Jack", "111"]
        },
        {
            "category": "B/BB",
            "name": ["Bob", "333"]
        },
        {
            "category": "C",
            "name": ["Cadel", "444"]
        },
        {
            "category": "C",
            "name": ["CadelTor", "555"]
        },
        {
            "category": "C",
            "name": ["Common", "666"]
        },
        {
            "category": "D/DD/DDD",
            "name": ["Dante", "888"]
        }
    ]
    mTree = MenuTree(entities)
    mTree.printTree()


if __name__ == '__main__':
    test()
