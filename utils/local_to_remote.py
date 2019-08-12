"""
提取本地114gh数据，存入到服务器10.20.31.14 mongodb 的 kidney数据库中
"""
import pymongo


class Extract(object):
    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['114gh']
        self.collection_114gh = self.db['114gh']
        self.collection_114yygh = self.db['114yygh_copy']

    def extract_data(self):
        """
        提取不重复姓名
        :return:
        """
        pass
