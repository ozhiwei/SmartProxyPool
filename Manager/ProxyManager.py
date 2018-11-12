# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyManager.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
-------------------------------------------------
"""
__author__ = 'JHao'

import random

from Util import EnvUtil
from DB.DbClient import DbClient
from Util.GetConfig import config
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy
from Log.LogManager import log


class ProxyManager(object):
    """
    ProxyManager
    """
    raw_proxy_name = "raw_proxy"
    useful_proxy_name = "useful_proxy"


    def __init__(self):
        self.db = DbClient()
        self.raw_proxy_queue = 'raw_proxy'
        self.useful_proxy_queue = 'useful_proxy'

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter
        :return:
        """
        for proxyGetter in config.proxy_getter_functions:
            try:
                log.info("Fetch Proxy Start, func:{func}".format(func=proxyGetter))

                total = 0
                succ = 0
                fail = 0
                for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
                    # 挨个存储 proxy，优化raw 队列的 push 速度，进而加快 check proxy 的速度
                    proxy = proxy.strip()
                    if proxy and verifyProxyFormat(proxy) and not self.checkRawProxyExists(proxy):
                        self.saveRawProxy(proxy)
                        succ = succ + 1
                        log.debug('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                    else:
                        fail = fail + 1
                        log.error('{func}: fetch proxy {proxy} error'.format(func=proxyGetter, proxy=proxy))

                    total = total + 1
                
                log.info("fetch proxy end, func:{func}, total:{total}, succ:{succ} fail:{fail}".format(func=proxyGetter, total=total, succ=succ, fail=fail))

            except Exception as e:
                log.error("func_name:{func} fetch proxy fail, error:{error}".format(func=proxyGetter, error=e))
                continue

    def get(self):
        """
        return a useful proxy
        :return:
        """
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
        # return self.db.pop()

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if EnvUtil.PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

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

    def getSampleUsefulProxy(self, **kwargs):
        result = self.db.getSampleUsefulProxy(**kwargs)
        return result

    def deleteRawProxy(self, proxy):
        self.db.deleteRawProxy(proxy)

    def saveRawProxy(self, proxy):
        self.db.saveRawProxy(proxy)

    def saveUsefulProxy(self, proxy):
        self.db.saveUsefulProxy(proxy)

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


if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
