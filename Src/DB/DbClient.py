# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import sys
import time

from Config import ConfigManager
from Util.utilClass import Singleton
from DB.MongodbClient import MongodbClient
from Log.LogManager import log

class DocsModel(object):
    docs_name = "test"

    def __init__(self):
        db_name = ConfigManager.bconfig.setting.get("db_name")
        db_host = ConfigManager.bconfig.setting.get("db_host")
        db_port = ConfigManager.bconfig.setting.get("db_port")
        db_username = ConfigManager.bconfig.setting.get("db_user")
        db_password = ConfigManager.bconfig.setting.get("db_pass")

        self.mc = MongodbClient(
            host=db_host,
            port=db_port,
            db_name=db_name,
            docs_name=self.docs_name,
            username=db_username,
            password=db_password,
        )

class UsefulProxyDocsModel(DocsModel):
    docs_name = "useful_proxy"

    def getAll(self):
        result = self.mc.find()
        return result

    def cleanUsefulProxy(self, **kwargs):
        result = 0
        hold_number = kwargs.get("hold_number")

        query = {"total": {"$ne": 0}}
        total_number = self.mc.count(query)
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


            items = self.mc.aggregate(operation_list)
            result = len(items)
            for item in items:
                query = {
                    "_id": item["_id"]
                }
                self.mc.delete(query)

        return result

    def cleanRawProxy(self, **kwargs):

        query = {
            "health": {
                "$lt": 1
            }
        }

        data = self.mc.delete(query)
        result = data['n']

        return result

    def getAllValidUsefulProxy(self, **kwargs):
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
        result = self.mc.aggregate(operation_list)

        return result

    def getAllUsefulProxy(self, **kwargs):
        result = self.getAll()
        return result

    def checkProxyExists(self, proxy):
        query = {"proxy": proxy}
        result = self.mc.exists(query)
        return result

    def checkUsefulProxyExists(self, proxy):
        result = self.checkProxyExists(proxy)
        return result

    # TODO: refine function
    def getSampleUsefulProxy(self, **kwargs):
        https = kwargs.get("https", None)
        proxy_region = kwargs.get("proxy_region", None)
        proxy_type = kwargs.get("proxy_type", None)

        result = None
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
        data = self.mc.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    def getProxyNum(self):
        result = self.mc.count()
        return result

    def saveUsefulProxy(self, data):
        self.mc.insert(data)

    def updateUsefulProxy(self, proxy, data):
        query = {"proxy": proxy}
        self.mc.update(query, data)

    def deleteUsefulProxy(self, proxy):
        query = {"proxy": proxy}
        self.mc.delete(query)

    def tickUsefulProxyVaildSucc(self, proxy):
        now_time = int(time.time())
        query = {"proxy": proxy}
        data = { 
            "$inc": {"succ": 1, "keep_succ": 1},
            "$set": {"last_status": "succ", "last_succ_time": now_time},
        }
        self.mc.upsert(query, data)

    def tickUsefulProxyVaildFail(self, proxy):
        query = {"proxy": proxy}
        data = { 
            "$inc": {"fail": 1},
            "$set": {"last_status": "fail", "keep_succ": 0},
        }
        self.mc.upsert(query, data)

    def tickUsefulProxyVaildTotal(self, proxy):
        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.mc.upsert(query, data)

class RawProxyDocsModel(DocsModel):
    docs_name = "raw_proxy"

    def getAll(self):
        result = self.mc.find()
        return result

    def getAllRawProxy(self, **kwargs):
        result = self.getAll()
        return result

    def cleanRawProxy(self, **kwargs):

        query = {
            "health": {
                "$lt": 1
            }
        }

        data = self.mc.delete(query)
        result = data['n']

        return result

    def checkProxyExists(self, proxy):
        query = {"proxy": proxy}
        result = self.mc.exists(query)
        return result

    def checkRawProxyExists(self, proxy):
        result = self.checkProxyExists(proxy)
        return result

    def getProxyNum(self):
        result = self.mc.count()
        return result

    def saveRawProxy(self, data):
        result = self.mc.insert(data)
        return result

    def deleteRawProxy(self, proxy):
        query = {"proxy": proxy}
        result = self.mc.delete(query)
        return result

    def tickRawProxyVaildFail(self, proxy):
        query = {"proxy": proxy}
        data = {'$inc': {'health': -1}}
        self.mc.upsert(query, data)

if __name__ == "__main__":
    pass
