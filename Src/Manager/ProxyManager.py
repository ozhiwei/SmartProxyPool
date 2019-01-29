# -*- coding: utf-8 -*-
# !/usr/bin/env python

import random

import datx
import time

from Util import EnvUtil
from DB.DbClient import UsefulProxyDocsModel, RawProxyDocsModel
from Config import ConfigManager
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy
from Log.LogManager import log

class ProxyManager(object):

    def __init__(self):
        self.useful_proxy = UsefulProxyDocsModel()
        self.raw_proxy = RawProxyDocsModel()
        self.datx = datx.City("Data/17monipdb.datx")

    def cleanUsefulProxy(self, **kwargs):
        result = self.useful_proxy.cleanUsefulProxy(**kwargs)
        return result

    def cleanRawProxy(self, **kwargs):
        result = self.raw_proxy.cleanRawProxy(**kwargs)
        return result

    def getAllValidUsefulProxy(self, **kwargs):
        result = self.useful_proxy.getAllValidUsefulProxy(**kwargs)
        return result

    def getAllUsefulProxy(self, **kwargs):
        result = self.useful_proxy.getAllUsefulProxy(**kwargs)
        return result

    def getAllRawProxy(self):
        result = self.raw_proxy.getAllRawProxy()
        return result

    def checkRawProxyExists(self, proxy):
        result = self.raw_proxy.checkRawProxyExists(proxy)
        return result

    def checkUsefulProxyExists(self, proxy):
        result = self.useful_proxy.checkUsefulProxyExists(proxy)
        return result

    def getSampleUsefulProxy(self, **kwargs):
        result = self.useful_proxy.getSampleUsefulProxy(**kwargs)

        return result

    def deleteRawProxy(self, proxy):
        self.raw_proxy.deleteRawProxy(proxy)

    def saveRawProxy(self, proxy):
        data = {
            "proxy": proxy,
            "health": ConfigManager.dbconfig.setting.get("init_raw_proxy_health")
        }
        self.raw_proxy.saveRawProxy(data)

    def getProxyRegion(self, ip):
        data = self.datx.find(ip)
        region_list = data[:3]
        result = []
        for item in region_list:
            if item and item not in result:
                result.append(item)

        return result

    def saveUsefulProxy(self, proxy_info):
        region_list = self.getProxyRegion(proxy_info.ip)
        now_time = int(time.time())

        data = {
            "proxy": proxy_info.address, 
            "succ": 1,
            "keep_succ": 1,
            "fail": 0,
            "total": 1,
            "https": proxy_info.https,
            "proxy_type": proxy_info.type,
            "region_list": region_list,
            "last_status": "succ",
            "last_succ_time": now_time,
            
        }

        self.useful_proxy.saveUsefulProxy(data)

    def updateUsefulProxy(self, proxy_item, proxy_info):
        data = {
            "$set": {
                "proxy_type": proxy_info.type,
            }
        }

        # https 的请求可能会失败, 所以这里不直接用新的 proxy_info.https 覆盖旧的字段.
        if proxy_item.get("https") == False and proxy_info.https != False:
            data["$set"]["https"] = proxy_info.https

        self.useful_proxy.updateUsefulProxy(proxy_info.address, data)

    def deleteUsefulProxy(self, proxy):
        self.useful_proxy.deleteUsefulProxy(proxy)

    def tickUsefulProxyVaildSucc(self, proxy):
        self.useful_proxy.tickUsefulProxyVaildSucc(proxy)

    def tickUsefulProxyVaildFail(self, proxy):
        self.useful_proxy.tickUsefulProxyVaildFail(proxy)

    def tickUsefulProxyVaildTotal(self, proxy):
        self.useful_proxy.tickUsefulProxyVaildTotal(proxy)

    def tickRawProxyVaildFail(self, proxy):
        self.raw_proxy.tickRawProxyVaildFail(proxy)

    def getProxyNumber(self):
        total_raw_proxy = self.getRawProxyNumber()
        total_useful_queue = self.getUsefulProxyNumber()
        result = {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}
        return result

    def getRawProxyNumber(self):
        result = self.raw_proxy.getProxyNum()
        return result

    def getUsefulProxyNumber(self):
        result = self.useful_proxy.getProxyNum()
        return result

proxy_manager = ProxyManager()

if __name__ == '__main__':
    # proxy_manager.refresh()
    pass
