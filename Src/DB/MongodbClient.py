# coding: utf-8

from pymongo import MongoClient


class MongodbClient(object):
    db_name = "proxy"

    def __init__(self, host, port, db_name, docs_name, **kwargs):
        self.conn = MongoClient(host, port, **kwargs)
        self.db = self.conn[db_name]
        self.docs = self.db[docs_name]

    def find_one(self, query):
        result = self.docs.find_one(query)
        return result

    def insert(self, data):
        result = self.docs.insert(data)
        return result

    def aggregate(self, operation_list):
        result = list(self.docs.aggregate(operation_list))
        return result

    def delete(self, query):
        result = self.docs.remove(query)
        return result

    def find(self, query):
        result = list(self.docs.find(query))
        return result

    def update(self, query, data):
        result = self.docs.update(query, data)
        return result

    def upsert(self, query, data):
        result = self.docs.update(query, data, upsert=True)
        return result

    def exists(self, query):
        result = False
        data = self.find_one(query)
        if data:
            result = True

        return result

    def count(self, query={}):
        result = self.docs.count(query)
        return result

if __name__ == "__main__":
    # db = MongodbClient('first', 'localhost', 27017)
    # db.put('127.0.0.1:1')
    # db2 = MongodbClient('second', 'localhost', 27017)
    # db2.put('127.0.0.1:2')
    # print(db.pop())
    pass
