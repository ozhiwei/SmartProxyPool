# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import sys
import time

from Config.ConfigManager import config
from Util.utilClass import Singleton
from DB.MongodbClient import MongodbClient
from Log.LogManager import log

class DbClient(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.__initDbClient()

    def __initDbClient(self):
        db_name = config.DB.name
        db_host = config.DB.host
        db_port = config.DB.port
        db_username = config.DB.username
        db_password = config.DB.password

        self.client = MongodbClient(name=db_name,
                                    host=db_host,
                                    port=db_port,
                                    username=db_username,
                                    password=db_password,)

    def getAll(self):
        return self.client.getAll()

    def changeTable(self, name):
        self.client.changeTable(name)

    def cleanProxy(self, **kwargs):
        result = 0
        hold_number = kwargs.get("hold_number")

        query = {"total": {"$ne": 0}}
        total_number = self.client.getCount(query)
        clean_number = total_number - hold_number

        if clean_number > 0 and hold_number != -1:
            operation_list = [
                {
                    "$match": query,
                },
                {
                    "$project": { "total": 1, "disable_rate": { "$divide": ["$fail", "$total"] } },
                },
                {
                    "$sort": { "disable_rate": -1, "total": -1 },
                },
                {
                    "$limit": clean_number,
                },
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

    def getAllValidUsefulProxy(self, **kwargs):
        table_name = "useful_proxy"
        self.changeTable(table_name)

        https = kwargs.get("https", None)
        proxy_region = kwargs.get("proxy_region", None)
        proxy_type = kwargs.get("proxy_type", None)

        result = []
        operation_list = [
            {
                "$match": { "total": { "$ne": 0 } }
            }
        ]

        if https:
            operation_list[0]["$match"]["https"] = { "$eq": https }

        if proxy_type:
            operation_list[0]["$match"]["proxy_type"] = { "$eq": proxy_type }

        if proxy_region:
            operation_list[0]["$match"]["region_list"] = { "$in": [proxy_region] }

        log.debug("getAllValidUsefulProxy, operation_list:{operation_list}, ".format(operation_list=str(operation_list)))
        result = self.client.aggregate(operation_list)

        return result

    def getUsefulProxyStat(self, **kwargs):
        table_name = "useful_proxy"
        self.changeTable(table_name)

        result = []
        operation_list = [
            {
                "$match": { "total": { "$ne": 0 } },
            }
        ]

        opertaion = {
            "$project": {
                "https": 1,
                "proxy_type": 1,
                "region_list": 1,
                "last_status": 1,
                "available_rate": { "$divide": ["$succ", "$total"] }
            }
        }
        operation_list.append(opertaion)

        log.debug("getAllUsefulProxy, operation_list:{operation_list}, ".format(operation_list=str(operation_list)))
        result = self.client.aggregate(operation_list)

        return result

    # def getAllProxy(self, **kwargs):
    #     table_name = "raw_proxy"
    #     self.changeTable(table_name)

    #     result = self.client.getAll()
    #     return result

    def getAllUsefulProxy(self, **kwargs):
        table_name = "useful_proxy"
        self.changeTable(table_name)

        result = self.client.getAll()
        return result

    def getAllRawProxy(self):
        table_name = "raw_proxy"
        self.changeTable(table_name)

        result = self.client.getAll()
        return result

    def checkProxyExists(self, proxy):
        query = {"proxy": proxy}
        result = self.client.exists(query)
        return result

    def checkRawProxyExists(self, proxy):
        result = self.checkProxyExists(proxy)
        return result

    def checkUsefulProxyExists(self, proxy):
        result = self.checkProxyExists(proxy)
        return result

    def getQualityProxy(self, **kwargs):
        https = kwargs.get("https", None)
        token = kwargs.get("token", None)
        proxy_region = kwargs.get("proxy_region", None)
        proxy_type = kwargs.get("type", None)

        result = None
        table_name = "useful_proxy"
        self.client.changeTable(table_name)
        operation_list = [
            {
                "$match": {
                    "total": { "$ne": 0},  
                    "last_status": { "$eq": "succ" },
                },
            },
            {
                "$project": { "proxy": 1, "available_rate": { "$divide": ["$succ", "$total"] } }
            },
            { 
                "$sort": { "available_rate": -1 }
            },
            {
                "$limit": 1
            }
        ]

        if https:
            operation_list[0]["$match"]["https"] = { "$eq": https }

        if proxy_type:
            operation_list[0]["$match"]["proxy_type"] = { "$eq": proxy_type }

        if token:
            operation_list[0]["$match"]["used_token_list"] = { "$nin": [token] }

        if proxy_region:
            operation_list[0]["$match"]["region_list"] = { "$in": [proxy_region] }



        log.debug("getQualityProxy, operation_list:{operation_list}".format(operation_list=str(operation_list)))
        data = self.client.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    # TODO: refine function
    def getSampleUsefulProxy(self, **kwargs):
        https = kwargs.get("https", None)
        proxy_region = kwargs.get("proxy_region", None)
        proxy_type = kwargs.get("proxy_type", None)

        result = None
        table_name = "useful_proxy"
        self.client.changeTable(table_name)
        operation_list = 	[
            {
                "$match": {
                    "total": { "$ne": 0},  
                    "last_status": { "$eq": "succ" },
                }
            },
            {
                "$sample": { "size": 1}
            }
        ]

        if https:
            operation_list[0]["$match"]["https"] = { "$eq": https }

        if proxy_type:
            operation_list[0]["$match"]["proxy_type"] = { "$eq": proxy_type }

        if proxy_region:
            operation_list[0]["$match"]["region_list"] = { "$in": [proxy_region] }



        log.debug("getSampleUsefulProxy, operation_list:{operation_list}, ".format(operation_list=str(operation_list)))
        data = self.client.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    def addTokenToProxy(self, proxy, token):
        query = {"proxy": proxy}
        update = { "$push": { "used_token_list": token } }
        self.client.upsert(query, update)

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
        number = self.client.getCount()

        return number

    def saveRawProxy(self, proxy, data):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        self.client.put(query, data)

    def saveUsefulProxy(self, proxy, data):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.put(query, data)

    def updateUsefulProxy(self, proxy, data):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.update(query, data)

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

        now_time = int(time.time())
        query = {"proxy": proxy}
        data = { 
            "$inc": {"succ": 1},
            "$set": {"last_status": "succ", "last_succ_time": now_time},
        }
        self.client.upsert(query, data)

    def tickUsefulProxyVaildFail(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = { 
            "$inc": {"fail": 1},
            "$set": { "last_status": "fail"},
        }
        self.client.upsert(query, data)

    def tickUsefulProxyVaildTotal(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.client.upsert(query, data)

    def tickRawProxyVaildSucc(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'succ': 1}}
        self.client.upsert(query, data)

    def tickRawProxyVaildFail(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'fail': 1}}
        self.client.upsert(query, data)

    def tickRawProxyVaildTotal(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.client.upsert(query, data)

if __name__ == "__main__":
    pass
