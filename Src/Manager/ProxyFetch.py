# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading

from Manager.ProxyManager import ProxyManager
from ProxyGetter.getFreeProxy import GetFreeProxy
from Log.LogManager import log
from Config.ConfigManager import config
from Util.utilFunction import verifyProxyFormat

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

# 这样的实现多线程有问题, 后期无法扩展到独立的机器上.
# must call classmethod initQueue before
class ProxyFetch(threading.Thread):
    queue = Queue()

    def __init__(self, **kwargs):
        super(ProxyFetch, self).__init__(**kwargs)
        self.proxy_manager = ProxyManager()

    @classmethod 
    def initQueue(cls):
        items = config.GetConfigGroupList("ProxyFetch")
        for item in items:
            cls.queue.put(item["setting_name"])

    def run(self):
        while self.queue.qsize():
            func_name = self.queue.get()
            try:
                start_time = time.time()
                log.debug("Fetch Proxy [{func_name}] Start".format(func_name=func_name))

                total = 0
                succ = 0
                fail = 0
                for proxy in getattr(GetFreeProxy, func_name.strip())():
                    proxy = proxy.strip()
                    if proxy and verifyProxyFormat(proxy) and \
                    not self.proxy_manager.checkRawProxyExists(proxy) and \
                    not self.proxy_manager.checkUsefulProxyExists(proxy):

                        self.proxy_manager.saveRawProxy(proxy)
                        succ = succ + 1
                        log.debug('{func_name}: fetch proxy {proxy} succ'.format(func_name=func_name, proxy=proxy))
                    else:
                        fail = fail + 1
                        log.debug('{func_name}: fetch proxy {proxy} fail'.format(func_name=func_name, proxy=proxy))

                    total = total + 1
                
                end_time = time.time()
                elapsed_time = int(end_time - start_time)
                log.info("Fetch Proxy [{func_name}] Finish, total:{total}, succ:{succ} fail:{fail} elapsed_time:{elapsed_time}s".format(func_name=func_name, total=total, succ=succ, fail=fail, elapsed_time=elapsed_time))

            except Exception as e:
                log.error("func_name:{func_name} fetch proxy fail, error:{error}s".format(func_name=func_name, error=e))

            self.queue.task_done()

if __name__ == "__main__":
    ProxyFetch.initQueue()

    t_list = []
    for _ in range(10):
        t = ProxyFetch()
        t_list.append(t)

    for t in t_list:
        t.daemon = True
        t.start()

    for t in t_list:
        t.join()