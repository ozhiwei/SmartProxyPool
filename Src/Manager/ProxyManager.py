# -*- coding: utf-8 -*-
# !/usr/bin/env python

import random

import datx

from Util import EnvUtil
from DB.DbClient import DbClient
from Config.ConfigManager import config
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy
from Log.LogManager import log

class ProxyManager(object):
    raw_proxy_name = "raw_proxy"
    useful_proxy_name = "useful_proxy"


    def __init__(self):
        self.db = DbClient()
        self.raw_proxy_queue = 'raw_proxy'
        self.useful_proxy_queue = 'useful_proxy'
        self.datx = datx.City("Data/17monipdb.datx")

    # def get(self):
    #     item = None
    #     item_list = []
    #     self.db.changeTable(self.useful_proxy_queue)

    #     item_dict = self.db.getAll()
    #     if item_dict:
    #         if EnvUtil.PY3:
    #             item_list = list(item_dict.keys())
    #         else:
    #             item_list = item_dict.keys()

    #     if item_list:
    #         item = random.choice(item_list)

    #     log.debug('Get Random Proxy {item} of {total}'.format(item=item, total=len(item_list)))
    #     return item

    # def getAll(self):
    #     self.db.changeTable(self.useful_proxy_queue)
    #     item_dict = self.db.getAll()
    #     if EnvUtil.PY3:
    #         return list(item_dict.keys()) if item_dict else list()
    #     return item_dict.keys() if item_dict else list()

    def cleanUsefulProxy(self, **kwargs):
        result = self.db.cleanUsefulProxy(**kwargs)
        return result

    def cleanRawProxy(self, **kwargs):
        result = self.db.cleanRawProxy(**kwargs)
        return result

    def getUsefulProxyStat(self, **kwargs):
        result = self.db.getUsefulProxyStat(**kwargs)
        return result

    def getAllValidUsefulProxy(self, **kwargs):
        result = self.db.getAllValidUsefulProxy(**kwargs)
        return result

    def getAllUsefulProxy(self, **kwargs):
        result = self.db.getAllUsefulProxy(**kwargs)
        return result

    def getAllRawProxy(self):
        result = self.db.getAllRawProxy()
        return result

    def checkRawProxyExists(self, proxy):
        result = self.db.checkRawProxyExists(proxy)
        return result

    def checkUsefulProxyExists(self, proxy):
        result = self.db.checkUsefulProxyExists(proxy)
        return result

    def getSampleRawProxy(self):
        result = self.db.getSampleRawProxy()
        return result

    def getQualityProxy(self, **kwargs):
        result = self.db.getQualityProxy(**kwargs)

        if result:
            proxy = result["proxy"]

            token = kwargs.get("token", None)
            if proxy and token:
                self.db.addTokenToProxy(proxy, token)

        return result

    def getSampleProxy(self, **kwargs):
        result = self.db.getSampleUsefulProxy(**kwargs)

        return result

    def getSampleUsefulProxy(self, **kwargs):
        result = self.db.getSampleUsefulProxy(**kwargs)

        return result

    def deleteRawProxy(self, proxy):
        self.db.deleteRawProxy(proxy)

    def saveRawProxy(self, proxy):
        data = {
            "proxy": proxy,
            "fail": 0, 
            "total": 0,
        }
        self.db.saveRawProxy(proxy, data)

    def getProxyRegion(self, ip):
        data = self.datx.find(ip)
        region_list = data[:3]
        result = []
        for item in region_list:
            if item and item not in result:
                result.append(item)

        return result

    # TODO: 逻辑应该有问题, 但不确定
    # http是可用的才会保存https, 会不会有只开通https的代理呢?
    def saveUsefulProxy(self, proxy):
        region_list = self.getProxyRegion(proxy.ip)

        data = {
            "proxy": proxy.address, 
            "succ": 1,
            "fail": 0,
            "total": 1,
            "https": proxy.https,
            "proxy_type": proxy.type,
            "region_list": region_list,
        }

        self.db.saveUsefulProxy(proxy.address, data)

    def deleteUsefulProxy(self, proxy):
        self.db.deleteUsefulProxy(proxy)

    def tickUsefulProxyVaildSucc(self, proxy):
        self.db.tickUsefulProxyVaildSucc(proxy)

    def tickUsefulProxyVaildFail(self, proxy):
        self.db.tickUsefulProxyVaildFail(proxy)

    def tickUsefulProxyVaildTotal(self, proxy):
        self.db.tickUsefulProxyVaildTotal(proxy)

    def tickRawProxyVaildSucc(self, proxy):
        self.db.tickRawProxyVaildSucc(proxy)

    def tickRawProxyVaildFail(self, proxy):
        self.db.tickRawProxyVaildFail(proxy)

    def tickRawProxyVaildTotal(self, proxy):
        self.db.tickRawProxyVaildTotal(proxy)

    def getProxyNumber(self):
        total_raw_proxy = self.getRawProxyNumber()
        total_useful_queue = self.getUsefulProxyNumber()
        result = {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}
        return result

    def getRawProxyNumber(self):
        num = self.db.getProxyNum(self.raw_proxy_name)
        return num

    def getUsefulProxyNumber(self):
        num = self.db.getProxyNum(self.useful_proxy_name)
        return num

proxy_manager = ProxyManager()

if __name__ == '__main__':
    proxy_manager.refresh()
