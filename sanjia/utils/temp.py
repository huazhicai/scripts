import pymongo


class MongoToMongo(object):
    """
    mongo数据转移
    """
    def __init__(self):
        self.local_client = pymongo.MongoClient('localhost')
        self.local_db = self.local_client['kidney']
        self.local_col = self.local_db['three_bj']

        self.remote_client = pymongo.MongoClient(host='1.tcp.cpolar.io', port=10090)
        # self.remote_client = pymongo.MongoClient('10.0.31.20')
        self.remote_db = self.remote_client['kidney']
        self.remote_col = self.remote_db['official']

    def read_and_write(self):
        for item in self.local_col.find():
            self.remote_col.insert_one(item)
            print(item)


if __name__ == '__main__':
    obj = MongoToMongo()
    obj.read_and_write()
