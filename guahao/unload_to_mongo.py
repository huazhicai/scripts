"""
联合更改字段
"""
import pymongo


class UnloadMongo(object):
    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['114gh']
        self.collection = self.db['114yygh_copy']

        self.collection_114yygh = self.db['114yygh']


if __name__ == '__main__':
    load = UnloadMongo()
    for i in load.collection.find({}):
        load.collection_114yygh.update_one({'name': i['name']}, {'$set': {'outpatient_info': i['outpatient_info']}})
        print(i['outpatient_info'])
