import pymongo
import requests
from pyquery import PyQuery as pq
import os, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'
}

MONGO_URL = '10.0.31.20'
PORT = 27017

# MONGO_DB = 'kidney'
MONGO_DB = 'test'
COLLECTION = 'official'

client = pymongo.MongoClient(host=MONGO_URL, port=PORT, connect=False)
db = client[MONGO_DB]
collection = db[COLLECTION]


def get_resp(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except ConnectionError as e:
        print('get_resp:', repr(e))


def save_to_mongo(result):
    if result['link']:
        # collection.insert_one(result)
        collection.update_one({'link': result['link']}, {'$set': result}, True)
        print(result)
