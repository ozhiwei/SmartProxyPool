# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import sys
import time

from Config import ConfigManager
from Util.utilClass import Singleton
from DB.MongodbClient import MongodbClient
from Log.LogManager import log
from Manager import ProxyManager

class DocsModel(object):
    docs_name = "test"

    def __init__(self):
        db_name = ConfigManager.base_config.setting.get("db_name")
        db_host = ConfigManager.base_config.setting.get("db_host")
        db_port = ConfigManager.base_config.setting.get("db_port")
        db_username = ConfigManager.base_config.setting.get("db_user")
        db_password = ConfigManager.base_config.setting.get("db_pass")

        self.mc = MongodbClient(
            host=db_host,
            port=db_port,
            db_name=db_name,
            docs_name=self.docs_name,
            username=db_username,
            password=db_password,
        )

def parse_regin_to_mongo(region_str):
    if region_str.startswith('!'):
        return { "$nin": [region_str[1:]] } 
    else:
        return { "$in": [region_str] }

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
        region = kwargs.get("region", None)
        type_ = kwargs.get("type", None)

        result = []
        operation_list = [
            {
                "$match": { "total": { "$ne": 0 } }
            }
        ]

        if https:
            operation_list[0]["$match"]["https"] = { "$eq": https }

        if type_:
            operation_list[0]["$match"]["type"] = { "$eq": type_ }

        if region:
            operation_list[0]["$match"]["region_list"] = parse_regin_to_mongo(region)

        log.debug("getAllValidUsefulProxy, operation_list:{operation_list}, ".format(operation_list=str(operation_list)))
        result = self.mc.aggregate(operation_list)

        return result

    def getHighQualityUsefulProxy(self, **kwargs):
        query = { "quality": { "$gt": -1 } }
        result= self.mc.find(query)
        return result

    def getLowQualityUsefulProxy(self, **kwargs):
        query = { "quality": { "$lt": 0 } }
        result= self.mc.find(query)
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
        region = kwargs.get("region", None)
        type_ = kwargs.get("type", None)

        result = None
        operation_list = 	[
            {
                "$match": {
                    "total": { "$ne": 0},  
                    "last_status": { "$eq": ProxyManager.PROXY_LAST_STATUS["SUCC"] },
                }
            },
            {
                "$sample": { "size": 1}
            }
        ]

        if https:
            operation_list[0]["$match"]["https"] = { "$eq": https }

        if type_:
            operation_list[0]["$match"]["type"] = { "$eq": type_ }

        if region: 
            operation_list[0]["$match"]["region_list"] = parse_regin_to_mongo(region)

        log.debug("getSampleUsefulProxy, operation_list:{operation_list}, ".format(operation_list=str(operation_list)))
        data = self.mc.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    def getVerifyUsefulProxy(self, **kwargs):
        now = int(time.time())
        query = {
            "next_verify_time": {
                "$lt": now
            }
        }
        result = self.mc.find(query)
        return result

    def getQualityUsefulProxy(self, **kwargs):
        https = kwargs.get("https", None)
        region = kwargs.get("region", None)
        type_ = kwargs.get("type", None)

        result = None
        operation_list = [
            {
                "$match": {
                    "total": { "$ne": 0 },
                }
            },
            {
                "$sort": { "quality": -1, "total": -1 },
            },
        ]

        if https:
            operation_list[0]["$match"]["https"] = { "$eq": https }

        if type_:
            operation_list[0]["$match"]["type"] = { "$eq": type_ }

        if region: 
            operation_list[0]["$match"]["region_list"] = parse_regin_to_mongo(region)

        log.debug("getSampleUsefulProxy, operation_list:{operation_list}, ".format(operation_list=str(operation_list)))
        result = self.mc.aggregate(operation_list)

        return result

    def getProxyNum(self):
        result = self.mc.count()
        return result

    def saveUsefulProxy(self, data):
        self.mc.insert(data)

    def updateUsefulProxy(self, proxy, data):
        query = {"proxy": proxy}
        self.updateProxy(query, data)

    def deleteUsefulProxy(self, proxy):
        query = {"proxy": proxy}
        self.mc.delete(query)

    def tickUsefulProxyVaildSucc(self, proxy):
        now_time = int(time.time())
        query = {"proxy": proxy}

        data = { 
            "$inc": {
                "succ": 1, 
                "keep_succ": 1,
            },
            "$set": {
                "last_status": ProxyManager.PROXY_LAST_STATUS["SUCC"], 
                "last_succ_time": now_time
            },
        }

        item = self.mc.find_one(query)
        if item["quality"] < 0:
            data["$set"]["quality"] = 1
        else:
            data["$inc"]["quality"] = 1 

        self.updateProxy(query, data)
    
    def getProxy(self, proxy):
        query = {"proxy": proxy}
        result = self.mc.find_one(query)
        return result

    def updateProxy(self, query, data):
        self.mc.upsert(query, data)

    def tickUsefulProxyVaildFail(self, proxy):
        query = {"proxy": proxy}
        data = { 
            "$inc": {
                "fail": 1,
                "quality": -1
            },
            "$set": {
                "last_status": ProxyManager.PROXY_LAST_STATUS["FAIL"], 
                "keep_succ": 0
            },
        }
        self.updateProxy(query, data)

    def tickUsefulProxyVaildTotal(self, proxy):
        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.updateProxy(query, data)

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
        self.updateProxy(query, data)

class DomainCounterDocsModel(DocsModel):
    docs_name = "domain_counter"

    def tickDomainRequestState(self, domain, code):
        query = {"domain": domain}
        data = {'$inc': {code: 1}}
        self.mc.upsert(query, data)

    def getDomainCounter(self, domain):
        query = {"domain": domain}
        result = self.mc.find_one(query)
        return result

class FetchersDocsModel(DocsModel):
    docs_name = "fetchers"

    def getAllFetcher(self):
        query = {}
        result = self.mc.find(query)
        return result

    def getFetcher(self, name):
        query = { "name": name }
        result = self.mc.find(query)
        return result

    def updateFetcher(self, name, data):
        query = {"name": name}
        self.mc.upsert(query, data)

if __name__ == "__main__":
    pass
