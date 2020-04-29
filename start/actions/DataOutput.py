# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by LiQing.
contact blacknepia@dingtail.com for more information
contact blacknepia@dingtail.com for more information
"""
from runtime.Action import Action
# from pyppeteer import launch
import json
import pymongo
import os
import asyncio


class ConsoleOutput(Action):
    """屏幕输出打印信息"""
    _id = '94ca1b06-e967-11e9-9ff5-8cec4bd887f3'
    node_info = {"args": [['prefix_optional_str', 'String', '39687032-47ab-413b-9b33-49fd3843109c'],
                          ['result_any', 'Any', '954f9c0c-c46f-4615-b411-9eea731b6e91'],
                          ['In', 'Event', '84e153c8-0acb-4cf8-89cc-426112f8689e']],
                 "returns": []}

    def __call__(self, args, io):
        prefix = args.get('prefix_optional_str', None)
        result = args['result_any']
        if prefix:
            print(prefix, end='')

        print(type(result))
        print(result)


class DataStore(Action):
    """节点中数据暂时存储"""
    _id = '9bdf5664-e967-11e9-8d60-8cec4bd887f3'
    node_info = {"args": [['data_any', 'Any', 'd887f4dc-003a-11ea-a4ba-8cec4bd83f9f'],
                          ['In', 'Event', 'ce693d31-f3a7-11e9-8654-8cec4bd887f3']],
                 "returns": [['data_any', 'Any', 'd887f4de-003a-11ea-a242-8cec4bd83f9f']]}

    def __call__(self, args, io):
        data = args['data_any']
        io.set_output('data_any', data)


class ConnectMongoDB(Action):
    _id = 'bbe99e18-e967-11e9-ad5f-87uav86c87f3'
    node_info = {"args": [['url_str', 'String', 'ce693d33-f3a7-11e9-123e-8cec4bd887f3'],
                          ['db_str', 'String', 'ce693d34-f3a7-11e9-6065-8cec4bd887f3'],
                          ['collection_str', 'String', 'ce613d35-f3a7-11e9-a4dd-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d37-f3a7-11e9-ba03-8cecja3287f3']],
                 "returns": [['collection', 'Any', 'ce69df37-f3a7-3219-ba03-8ce854al87f3'],
                              ['Out', 'Event', 'ce69df37-f3a7-0219-ba03-8c85421l87f3']]}
    def __call__(self, args, io):
        mongo_url = args['url_str']
        mongo_db = args['db_str']
        mongo_chart = args['collection_str']
        client = pymongo.MongoClient(mongo_url)
        db = client[mongo_db]
        collection = db[mongo_chart]

        io.set_output('collection', collection)
        io.push_event('Out')


class InsertToMongo(Action):
    """将数据存入Mongodb中"""
    _id = 'bbe99e18-e967-11e9-ad5f-8cec4bd887f3'
    node_info = {"args": [['url_str', 'String', 'ce693d33-f3a7-11e9-b0ce-8cec4bd887f3'],
                          ['db_str', 'String', 'ce693d34-f3a7-11e9-8965-8cec4bd887f3'],
                          ['collection_str', 'String', 'ce693d35-f3a7-11e9-a4dd-8cec4bd887f3'],
                          ['doc_dict', 'Dict', 'ce693d36-f3a7-11e9-acae-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d37-f3a7-11e9-ba03-8cec4bd887f3']],
                 "returns": []}

    mongo_url = '192.168.66.108'
    client = pymongo.MongoClient(mongo_url)

    def __call__(self, args, io):

        data = args['doc_dict']
        db_str = args['db_str']
        collection_str = args['collection_str']

        db = self.client[db_str]
        collection = db[collection_str]

        collection.insert_one(data)
        # if collection.insert_one(data):
        #     print(data)
        # else:
        #     print('Insert to mongodb failed!')

class GetMongoData(Action):
    """将数据存入Mongodb中"""
    _id = 'c1cdbb36-e967-11e9-b968-8cec4b20187f3'
    node_info = {"args": [['url_str', 'String', 'ce693d38-f3a7-11e9-8b6c-8cec4b32a7f3'],
                          ['db_str', 'String', 'ce693d39-f3a7-11e9-b1d1-8cecacf887f3'],
                          ['collection_str', 'String', 'ce693d3a-f3a7-11e9-9e85-8cec4bd8652f3'],
                          ['doc_dict', 'Dict', 'ce693d3b-f3a7-11e9-cfkf-8cec4bd887f3'],
                          ['query_key_str', 'String', 'ce693d3c-f3a7-11e9-b196-8cec4bd8jcnf3'],
                          ['In', 'Event', 'ce693d3d-f3a7-11e9-8a41-8cec4bd8321f3']],
                 "returns": [['output_data', 'Any', 'ce693d3c-f3a7-11e9-b196-8c2314d8jcnf3'],
                          ['Out', 'Event', 'ce693d3d-f3a7-11e9-8a41-8cec2143321f3']]}

    def __call__(self, args, io):
        mongo_url = args['url_str']
        mongo_db = args['db_str']
        mongo_chart = args['collection_str']
        display_key = args['query_key_str']

        client = pymongo.MongoClient(mongo_url)
        db = client[mongo_db]
        collection = db[mongo_chart]

        display = dict(zip(display_key, [1] * len(display_key)))

        # for doc in collection.find({}, {'patient_id': 1, 'yibanziliao': 1}):
        #     io.set_output('output_data', doc)
        #     io.push_event('Out1')
        # io.push_event('Out2')
        output = collection.find({}, {'patient_id':1, 'yibanziliao': 1, '_id': 0})
        io.set_output('output_data', output)
        io.push_event('Out')
            

class UpdateToMongo(Action):
    """将数据存入Mongodb中"""
    _id = 'c1cdbb36-e967-11e9-b968-8cec4bd887f3'
    node_info = {"args": [['url_str', 'String', 'ce693d38-f3a7-11e9-8b6c-8cec4bd887f3'],
                          ['db_str', 'String', 'ce693d39-f3a7-11e9-b1d1-8cec4bd887f3'],
                          ['collection_str', 'String', 'ce693d3a-f3a7-11e9-9e85-8cec4bd887f3'],
                          ['doc_dict', 'Dict', 'ce693d3b-f3a7-11e9-b796-8cec4bd887f3'],
                          ['query_key', 'Any', 'ce693d3c-f3a7-11e9-b196-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d3d-f3a7-11e9-8a41-8cec4bd887f3']],
                 "returns": []}
    def convert_xingbie(self, data):
        if data['yibanziliao']['xingbie'] == '男':
            data['yibanziliao']['xingbie'] = 1
        elif data['yibanziliao']['xingbie'] == '女':
            data['yibanziliao']['xingbie'] = 2

    def key_int_to_str(self, data):
      for key, val in data.items():
          if isinstance(val, dict):
              self.key_int_to_str(val)
          elif isinstance(val, list):
              for item in val:
                  self.key_int_to_str(item)
          else:
            if isinstance(key, int):
               data[str(key)] = val
               data.pop(key)


    def __call__(self, args, io):
        # print('call')
        mongo_url = args['url_str']
        mongo_db = args['db_str']
        mongo_chart = args['collection_str']
        data = args['doc_dict']
        query_key = args['query_key']
        # print(query_key, type(query_key))

        client = pymongo.MongoClient(mongo_url)
        db = client[mongo_db]
        collection = db[mongo_chart]
        try:
            self.convert_xingbie(data)
            collection.update_one({query_key: data[query_key]}, {'$set': data}, upsert=True)
            # self.key_int_to_str(data)
            # collection.insert_one(data)
            print('update to mongo successfully!')
        except Exception as e:
            print('Update to mongodb failed!', e)
            with open('monoerr.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                    

class SaveJsonFile(Action):
    """数据保存为json格式文件"""
    _id = '94ff84f8-e9a4-11e9-bbe0-f416630aacec'
    node_info = {"args": [['filename_str', 'String', 'ce693d3e-f3a7-11e9-8786-8cec4bd887f3'],
                          ['doc_dict', 'Dict', 'ce693d3f-f3a7-11e9-b1d1-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d40-f3a7-11e9-8e3d-8cec4bd887f3']],
                 "returns": []}

    def __call__(self, args, io):
        filename = args['filename_str'].strip()
        if filename.endswith('.txt'):
            filename = filename.strip('.txt')

        if not filename.endswith('.json'):
            filename = filename + '.json'

        data = args['doc_dict']
        file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files', filename)
        with open(file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')


class SaveTxtFile(Action):
    """数据保存为json格式文件"""
    _id = '94ff98f8-e9a4-11e9-bbe0-f414330aacec'
    node_info = {"args": [['filename_str', 'String', 'ce693d3e-f3a7-11e9-5466-8cec4bd887f3'],
                          ['doc', 'String', 'ce693d3f-f3a7-32e9-b1d1-8cec4bd557f3'],
                          ['In', 'Event', 'ce693d40-f3a7-11e9-8e3d-8cec4bd667f3']],
                 "returns": []}

    def __call__(self, args, io):
        filename = args['filename_str'].strip()

        if not filename.endswith('.txt'):
            filename = filename + '.txt'

        data = args['doc']
        file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files', filename)
        with open(file, 'w', encoding='utf-8') as f:
            f.write(data)


class FormatData(Action):
    """接收爬虫输出字典数据，转换为['name': some, 'value': other ]"""
    _id = 'af5b8e9a-ef20-11e9-9bb3-f416630aacec'
    node_info = {"args": [['doc_dict', 'Dict', 'ce693d4a-f3a7-11e9-a298-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d4b-f3a7-11e9-aef3-8cec4bd887f3']],
                 "returns": [['output_str', 'String', 'ce693d4c-f3a7-11e9-ac04-8cec4bd887f3'],
                             ['Out', 'Event', 'ce693d4d-f3a7-11e9-a090-8cec4bd887f3']]}

    def __call__(self, args, io):
        doc = args['doc_dict']
        output = []
        for key, value in doc.items():
            temp = {}
            temp['name'] = key
            temp['value'] = value
            output.append(temp)

        io.set_output('output_str', json.dumps(output).replace("'", '"'))
        io.push_event('Out')


class WithOpenTxt(Action):
    """将接受的数据写入本地，Txt格式"""
    _id = '9246b900-f3a1-11e9-86df-8cec4bd887f3'
    node_info = {"args": [['data_any', 'Any', '391c4b6a-f3a8-11e9-aef8-8cec4bd887f3'],
                          ['file_name_str', 'String', '391c4b6b-f3a8-11e9-8658-8cec4bd887f3'],
                          ['write_way_str', 'String', '391c4b6c-f3a8-11e9-b5cc-8cec4bd887f3'],
                          ['encoding_str', 'String', 'b56ad691-f3a8-11e9-aa1b-8cec4bd887f3'],
                          ['In', 'Event', '391c4b6d-f3a8-11e9-aaf0-8cec4bd887f3']],
                 "returns": []}

    def __call__(self, args, io):
        data = args['data_any']
        file_name = args['file_name_str']
        write_way = args['write_way_str']
        encoding = args['encoding_str']
        with open(file_name, write_way, encoding=encoding) as fp:
            fp.write(data)
