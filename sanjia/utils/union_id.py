"""
提取官网数据 Document '_id' 存入到对应的挂号信息文档中
"""

import pymongo


class Union(object):
    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db_official = self.client['kidney']
        self.db_gh = self.client['114gh']
        self.collection_official = self.db_official['three_bj']
        self.collection_gh = self.db_gh['114yygh']

    def extract_gh(self):
        for j in self.collection_gh.find({}, {'name': 1}):
            yield j


if __name__ == '__main__':
    union = Union()
    for j in union.extract_gh():
        resp = union.collection_official.find_one({'name': j['name']}, {'name': 1, 'hospital': 1})
        union_id = resp.get('_id', None) if resp else None
        union.collection_gh.update_one({'name': j['name']}, {'$set': {'union_id': union_id}})
