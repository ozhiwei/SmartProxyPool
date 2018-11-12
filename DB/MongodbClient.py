# coding: utf-8
"""
-------------------------------------------------
   File Name：    MongodbClient.py
   Description :  封装mongodb操作
   Author :       JHao netAir
   date：          2017/3/3
-------------------------------------------------
   Change Activity:
                   2017/3/3:
                   2017/9/26:完成对mongodb的支持
-------------------------------------------------
"""
__author__ = 'Maps netAir'

from pymongo import MongoClient


class MongodbClient(object):
    def __init__(self, name, host, port, **kwargs):
        self.name = name
        self.client = MongoClient(host, port, **kwargs)
        self.db = self.client.proxy

    def changeTable(self, name):
        self.name = name

    def get(self, query):
        data = self.db[self.name].find_one(query)
        return data

    def put(self, query, data):
        if self.db[self.name].find_one(query):
            return None
        else:
            self.db[self.name].insert(data)

    # unuseful function
    # def pop(self):
    #     data = list(self.db[self.name].aggregate([{'$sample': {'size': 1}}]))
    #     if data:
    #         data = data[0]
    #         value = data['proxy']
    #         self.delete(value)
    #         return {'proxy': value, 'value': data['num']}
    #     return None

    def aggregate(self, operation_list):
        data = list(self.db[self.name].aggregate(operation_list))
        return data

    def delete(self, query):
        self.db[self.name].remove(query)

    def getAll(self):
        data = self.db[self.name].find()
        result = { item['proxy']: item for item in data }
        return result

    def clean(self):
        self.client.drop_database('proxy')

    def delete_all(self):
        self.db[self.name].remove()

    def update(self, query, data):
        self.db[self.name].update(query, data)

    def exists(self, query):
        result = False
        data = self.get(query)
        if data:
            result = True

        return result

    def getNumber(self):
        return self.db[self.name].count()


if __name__ == "__main__":
    db = MongodbClient('first', 'localhost', 27017)
    # db.put('127.0.0.1:1')
    # db2 = MongodbClient('second', 'localhost', 27017)
    # db2.put('127.0.0.1:2')
    # print(db.pop())
