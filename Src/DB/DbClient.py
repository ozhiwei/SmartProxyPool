# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import sys

from Config.ConfigManager import config
from Util.utilClass import Singleton

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DbClient(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.__initDbClient()

    def __initDbClient(self):
        db_type = config.DB.type
        db_name = config.DB.name
        db_host = config.DB.host
        db_port = config.DB.port
        db_username = config.DB.username
        db_password = config.DB.password

        __type = None
        if "SSDB" == db_type:
            __type = "SsdbClient"
        elif "REDIS" == db_type:
            __type = "RedisClient"
        elif "MONGODB" == db_type:
            __type = "MongodbClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(db_type)
        self.client = getattr(__import__(__type), __type)(name=db_name,
                                                          host=db_host,
                                                          port=db_port,
                                                          username=db_username,
                                                          password=db_password)
    # unuseful function
    # def get(self, key, **kwargs):
    #     query = {"proxy": key}
    #     data = self.client.get(query)
    #     return data

    # unuseful function
    # def put(self, key, **kwargs):
    #     return self.client.put(key, **kwargs)

    # unuseful function
    # def update(self, query, data):
    #     return self.client.update(query, data)

    # unuseful function
    # def delete(self, key):
    #     return self.client.delete(key, **kwargs)

    # unuseful function
    # def exists(self, key, **kwargs):
    #     return self.client.exists(key, **kwargs)

    # unuseful function
    # def pop(self, **kwargs):
    #     return self.client.pop(**kwargs)

    def getAll(self):
        return self.client.getAll()

    def changeTable(self, name):
        self.client.changeTable(name)

    def cleanProxy(self, **kwargs):
        operation_list = [
            {
                "$match": {"total": { "$gte": kwargs.get("total") }},
            },
            {
                "$project": { "proxy": 1, "disable_rate": { "$divide": ["$fail", "$total"] } }
            },
            {
                "$match": { "disable_rate": { "$gte": kwargs.get("disable_rate")}}
            }
        ]

        items = self.client.aggregate(operation_list)
        result = len(items)
        for item in items:
            query = {
                "_id": item["_id"]
            }
            self.client.delete(query)

        return result


    def cleanUsefulProxy(self, **kwargs):
        table_name = "useful_proxy"
        self.changeTable(table_name)

        result = self.cleanProxy(**kwargs)

        return result


    def cleanRawProxy(self, **kwargs):
        table_name = "raw_proxy"
        self.changeTable(table_name)

        result = self.cleanProxy(**kwargs)

        return result


    # unuseful function
    # def getNumber(self):
    #     return self.client.getNumber()

    def getAllUsefulProxy(self):
        table_name = "useful_proxy"
        self.changeTable(table_name)

        result = self.client.getAll()
        return result

    def getAllRawProxy(self):
        table_name = "raw_proxy"
        self.changeTable(table_name)

        result = self.client.getAll()
        return result

    def checkRawProxyExists(self, proxy):
        query = {"proxy": proxy}
        self.client.exists(query)

    def getQualityProxy(self, https=False, token=None):
        result = None
        table_name = "useful_proxy"
        self.client.changeTable(table_name)
        operation_list = [
            {
                "$match": {"total": { "$ne": 0},  "https": { "$eq": https }, "used_token_list": { "$nin": [token] } },
            },
            {
                "$project": { "proxy": 1, "usable_rate": { "$divide": ["$succ", "$total"] } }
            },
            { 
                "$sort": { "usable_rate": -1 }
            },
            {
                "$limit": 1
            }
        ]

        data = self.client.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    # TODO: refine function
    def getSampleUsefulProxy(self, **kwargs):
        result = None
        table_name = "useful_proxy"
        self.client.changeTable(table_name)
        operation_list = 	[
            {
                "$match": {"https": { "$eq": kwargs.get("https", None) }},
            },
            {
                "$sample": { "size": 1}
            }
        ]

        data = self.client.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    def addProxyUsedToken(self, proxy, token):
        query = {"proxy": proxy}
        update = { "$push": { "used_token_list": token } }
        self.client.update(query, update)

    # TODO: refine function
    def getSampleRawProxy(self):
        result = None
        table_name = "raw_proxy"
        self.client.changeTable(table_name)
        operation_list = 	[
            {
                "$sample": { "size": 1}
            },
        ]
        data = self.client.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    def getProxyNum(self, table_name):
        self.client.changeTable(table_name)
        number = self.client.getNumber()

        return number

    def saveRawProxy(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        data = {"proxy": proxy, "succ": 0, "fail": 0, "total": 0}
        self.client.put(query, data)

    def saveUsefulProxy(self, proxy, data):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.put(query, data)

    def deleteUsefulProxy(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.delete(query)

    def deleteRawProxy(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.delete(query)

    def tickUsefulProxyVaildSucc(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'succ': 1}}
        self.client.update(query, data)

    def tickUsefulProxyVaildFail(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'fail': 1}}
        self.client.update(query, data)

    def tickUsefulProxyVaildTotal(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.client.update(query, data)

    def tickRawProxyVaildSucc(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'succ': 1}}
        self.client.update(query, data)

    def tickRawProxyVaildFail(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'fail': 1}}
        self.client.update(query, data)

    def tickRawProxyVaildTotal(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.client.update(query, data)

if __name__ == "__main__":
    pass
