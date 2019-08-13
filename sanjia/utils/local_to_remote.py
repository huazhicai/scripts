"""
读取本地MongoDB数据，存储到10.0.30.202服务器MongoDB
"""
import pymongo


class UnloadDate(object):
    def __init__(self):
        self.local_client = pymongo.MongoClient('localhost')
        self.local_db = self.local_client['114gh']
        self.local_collect = self.local_db['114yygh']

        self.remote_client = pymongo.MongoClient('mongodb://kidney:123456@10.0.30.202:27017')
        self.remote_db = self.remote_client['kidney']
        self.remote_collect = self.remote_db['guahao_info']

    def extract_data(self):
        for i in self.local_collect.find({}):
            yield i

    def save_data(self, result):
        self.remote_collect.insert_one(result)
        print(result)


if __name__ == '__main__':
    unload = UnloadDate()
    for j in unload.extract_data():
        unload.save_data(j)
