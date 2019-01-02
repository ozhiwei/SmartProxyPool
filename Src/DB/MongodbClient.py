# coding: utf-8

from pymongo import MongoClient


class MongodbClient(object):
    def __init__(self, name, host, port, **kwargs):
        self.name = name
        self.client = MongoClient(host, port, **kwargs)
        self.db = self.client.proxy

    def changeTable(self, name):
        self.name = name

    def get(self, query):
        result = self.db[self.name].find_one(query)
        return result

    def put(self, query, data):
        if self.db[self.name].find_one(query):
            return None
        else:
            self.db[self.name].insert(data)

    def aggregate(self, operation_list):
        result = list(self.db[self.name].aggregate(operation_list))
        return result

    def delete(self, query):
        result = self.db[self.name].remove(query)
        return result

    def getAll(self):
        result = []
        items = self.db[self.name].find()
        for item in items:
            result.append(item)

        return result

    def clean(self):
        self.client.drop_database('proxy')

    def delete_all(self):
        self.db[self.name].remove()

    def update(self, query, data):
        self.db[self.name].update(query, data)

    def upsert(self, query, data):
        self.db[self.name].update(query, data, upsert=True)

    def exists(self, query):
        result = False
        data = self.get(query)
        if data:
            result = True

        return result

    def getCount(self, query={}):
        result = self.db[self.name].count(query)
        return result

if __name__ == "__main__":
    db = MongodbClient('first', 'localhost', 27017)
    # db.put('127.0.0.1:1')
    # db2 = MongodbClient('second', 'localhost', 27017)
    # db2.put('127.0.0.1:2')
    # print(db.pop())
