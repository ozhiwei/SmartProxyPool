# -*- coding: utf-8 -*-
# !/usr/bin/env python

import random

import datx
import time

from Util import EnvUtil
from DB.DbClient import UsefulProxyDocsModel, RawProxyDocsModel, DomainCounterDocsModel, FetchersDocsModel
from Config import ConfigManager
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy
from Log.LogManager import log

PROXY_LAST_STATUS = {
    "UNKNOWN": 0,
    "SUCC": 1,
    "FAIL": 2,
}

PROXY_TYPE = {
    "UNKNOWN": 0,
    "CLEAR": 1,
    "ANONYMOUS": 2,
    "DYNAMIC": 3,
}

PROXY_HTTPS = {
    "UNKNOWN": 0,
    "ENABLE": 1,
    "DISABLE": 2,
}

IP_DATA_PATH = "Data/17monipdb.datx"

class ProxyManager(object):

    def __init__(self):
        self.useful_proxy = UsefulProxyDocsModel()
        self.raw_proxy = RawProxyDocsModel()
        self.domain_counter = DomainCounterDocsModel()
        self.fetchers = FetchersDocsModel()
        self.datx = datx.City(IP_DATA_PATH)

        self.quality_useful_proxy_list = []
        self.quality_domain_index = {}

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

    def getQualityUsefulProxy(self, **kwargs):
        count = kwargs.get("count", 1)
        domain = kwargs.get("domain", None)

        index = self.quality_domain_index.get(domain, 0)

        if index == 0:
            self.quality_useful_proxy_list = self.useful_proxy.getQualityUsefulProxy(**kwargs)

        index = (count-1) % len(self.quality_useful_proxy_list)
        self.quality_domain_index[domain] = index+1

        result = self.quality_useful_proxy_list[index]
        return result

    def deleteRawProxy(self, proxy):
        self.raw_proxy.deleteRawProxy(proxy)

    def saveRawProxy(self, proxy):
        data = {
            "proxy": proxy,
            "health": ConfigManager.setting_config.setting.get("init_raw_proxy_health")
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

    def saveUsefulProxy(self, proxy):
        ip = proxy.split(":")[0]
        region_list = self.getProxyRegion(ip)

        data = {
            "proxy": proxy, 
            "succ": 0,
            "keep_succ": 0,
            "fail": 0,
            "total": 0,
            "https": PROXY_HTTPS["UNKNOWN"],
            "type": PROXY_TYPE["UNKNOWN"],
            "region_list": region_list,
            "last_status": PROXY_LAST_STATUS["UNKNOWN"],
            "last_succ_time": 0,
            
        }

        self.useful_proxy.saveUsefulProxy(data)

    def updateUsefulProxy(self, item, info):
        data = {
            "$set": {}
        }

        if item.get("type") == PROXY_TYPE["UNKNOWN"]:
            data["$set"]["type"]: info.type

        if item.get("https") == PROXY_HTTPS["UNKNOWN"]:
            data["$set"]["https"] = info.https

        if len(data["$set"]) > 0:
            self.useful_proxy.updateUsefulProxy(info.address, data)

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

    def tickDomainRequestState(self, domain, code):
        self.domain_counter.tickDomainRequestState(domain, code)

    def getDomainCounter(self, domain):
        result = self.domain_counter.getDomainCounter(domain)
        return result


    def getAllFetcher(self):
        result = self.fetchers.getAllFetcher()
        return result

    def getFetcher(self, name):
        result = self.fetchers.getFetcher(name)
        return result


    def updateFetcher(self, name, data):
        self.fetchers.updateFetcher(name, data)

proxy_manager = ProxyManager()

if __name__ == '__main__':
    # proxy_manager.refresh()
    pass
