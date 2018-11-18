# -*- coding: utf-8 -*-
# !/usr/bin/env python

import random

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

    def get(self):
        item = None
        item_list = []
        self.db.changeTable(self.useful_proxy_queue)

        item_dict = self.db.getAll()
        if item_dict:
            if EnvUtil.PY3:
                item_list = list(item_dict.keys())
            else:
                item_list = item_dict.keys()

        if item_list:
            item = random.choice(item_list)

        log.debug('Get Random Proxy {item} of {total}'.format(item=item, total=len(item_list)))
        return item

    def getAll(self):
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if EnvUtil.PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

    def cleanUsefulProxy(self, **kwargs):
        result = self.db.cleanUsefulProxy(**kwargs)
        return result

    def cleanRawProxy(self, **kwargs):
        result = self.db.cleanRawProxy(**kwargs)
        return result

    def getAllUsefulProxy(self):
        result = self.db.getAllUsefulProxy()
        return result

    def getAllRawProxy(self):
        result = self.db.getAllRawProxy()
        return result

    def checkRawProxyExists(self, proxy):
        result = self.db.checkRawProxyExists(proxy)
        return result

    def getSampleRawProxy(self):
        result = self.db.getSampleRawProxy()
        return result

    def getQualityProxy(self, **kwargs):
        item = self.db.getQualityProxy(**kwargs)
        result = None

        if item:
            result = item["proxy"]

        token = kwargs.get("token", None)
        if token:
            self.db.addProxyUsedToken(result, token)

        log.debug("getQualityProxy, item:{item}".format(item=str(item)))

        return result

    def getSampleProxy(self, **kwargs):
        item = self.db.getSampleUsefulProxy(**kwargs)
        result = None
        if item:
            result = item["proxy"]

        log.debug("getSampleUsefulProxy, item:{item}".format(item=str(item)))

        return result

    # 准备删除
    def getSampleUsefulProxy(self, **kwargs):
        item = self.db.getSampleUsefulProxy(**kwargs)
        result = None
        if item:
            result = item["proxy"]

            token = kwargs.get("token", None)
            if token:
                self.db.addProxyUsedToken(result, token)

        log.debug("getSampleUsefulProxy, item:{item}".format(item=str(item)))

        return result

    def deleteRawProxy(self, proxy):
        self.db.deleteRawProxy(proxy)

    def saveRawProxy(self, proxy):
        self.db.saveRawProxy(proxy)

    # TODO: 逻辑应该有问题, 但不确定
    # http是可用的才会保存https, 会不会有只开通https的代理呢?
    def saveUsefulProxy(self, proxy, https=False):
        data = {"proxy": proxy, "succ": 1, "fail": 0, "total": 1, "https": https}
        self.db.saveUsefulProxy(proxy, data)

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
