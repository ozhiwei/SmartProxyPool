# -*- coding: utf-8 -*-
# !/usr/bin/env python

from gevent import monkey
monkey.patch_all()

import sys
sys.path.append("Src")
import time
import threading
import gevent

from Manager.ProxyManager import proxy_manager
from ProxyGetter.getFreeProxy import GetFreeProxy
from Log.LogManager import log
from Config import ConfigManager
from Util.utilFunction import verifyProxyFormat

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

# 这样的实现多线程有问题, 后期无法扩展到独立的机器上.
# must call classmethod initQueue before
class ProxyFetch(object):
    queue = Queue()

    @classmethod 
    def initQueue(cls):
        items = config.GetConfigGroupList("ProxyFetch")
        for item in items:
            cls.queue.put(item["setting_name"])

    def start(self):
        concurrency = ConfigManager.dbconfig.setting.get("fetch_new_proxy_concurrency")
        queue_size = self.queue.qsize()
        if concurrency > queue_size:
            spawn_num = queue_size
        else:
            spawn_num = concurrency

        greenlet_list = []
        for _ in range(spawn_num):
            greenlet_list.append(gevent.spawn(self.run))

        gevent.joinall(greenlet_list)

    def fetch(self):
        start_time = time.time()
        total = 0
        succ = 0
        fail = 0
        skip = 0

        func_name = self.queue.get()
        log.debug("fetch [{func_name}] proxy start".format(func_name=func_name))
        try:
            for proxy in getattr(GetFreeProxy, func_name.strip())():
                proxy = proxy.strip()
                if proxy and verifyProxyFormat(proxy) and \
                not proxy_manager.checkRawProxyExists(proxy) and \
                not proxy_manager.checkUsefulProxyExists(proxy):

                    proxy_manager.saveRawProxy(proxy)
                    succ = succ + 1
                    log.debug("fetch [{func_name}] proxy {proxy} succ".format(func_name=func_name, proxy=proxy))
                else:
                    skip = skip + 1
                    log.debug("fetch [{func_name}] proxy {proxy} skip".format(func_name=func_name, proxy=proxy))

                total = total + 1
        except Exception as e:
            log.debug("fetch [{func_name}] proxy {proxy} fail: {error}".format(func_name=func_name, proxy=proxy, error=e))
            fail = fail + 1

        end_time = time.time()
        elapsed_time = int(end_time - start_time)

        log.info("fetch [{func_name}] proxy finish, total:{total}, succ:{succ}, fail:{fail}, skip:{skip}, elapsed_time:{elapsed_time}s".format(func_name=func_name, total=total, succ=succ, fail=fail, skip=skip, elapsed_time=elapsed_time))

    def run(self):
        while self.queue.qsize():
            self.fetch()


            
if __name__ == "__main__":
    ProxyFetch.initQueue()
    t = ProxyFetch()
    t.start()