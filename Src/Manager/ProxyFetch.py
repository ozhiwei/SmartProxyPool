# -*- coding: utf-8 -*-
# !/usr/bin/env python

from gevent import monkey, pool
monkey.patch_all()

import sys
sys.path.append("Src")
import time
import threading
import gevent

from Manager import ProxyManager
# from ProxyGetter.getFreeProxy import GetFreeProxy
from Fetcher import FetcherManager
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
        fetchers = ProxyManager.proxy_manager.getExecFetcher()
        for fetcher in fetchers:
            cls.queue.put(fetcher)

    def start(self):
        self.start_time = int(time.time())
        concurrency = ConfigManager.setting_config.setting.get("fetch_new_proxy_concurrency")
        task_pool = pool.Pool(concurrency)

        queue_size = self.queue.qsize()
        if queue_size > 0:
            greenlet_list = []
            for _ in range(queue_size):
                greenlet_list.append(task_pool.spawn(self.fetch))

            gevent.joinall(greenlet_list)
        else:
            log.info("Not Have Fetcher Of Now, skip!")

    def fetch(self):
        start_time = time.time()
        total = 0
        succ = 0
        fail = 0
        skip = 0

        fetcher = self.queue.get()
        name = fetcher["name"]

        fetcher_class = FetcherManager.getFetcherClass(name)
        log.debug("fetch [{name}] proxy start".format(name=name))
        try:
            f = fetcher_class()
            for proxy in f.run():
                proxy = proxy.strip()
                if proxy and verifyProxyFormat(proxy) and \
                not ProxyManager.proxy_manager.checkUsefulProxyExists(proxy):

                    ProxyManager.proxy_manager.saveUsefulProxy(proxy)
                    succ = succ + 1
                    log.debug("fetch [{name}] proxy {proxy} succ".format(name=name, proxy=proxy))
                else:
                    skip = skip + 1
                    log.debug("fetch [{name}] proxy {proxy} skip".format(name=name, proxy=proxy))

                total = total + 1
        except Exception as e:
            log.error("fetch [{name}] proxy fail: {error}".format(name=name, error=e))
            fail = fail + 1

        self.queue.task_done()

        now = int(time.time())
        elapsed_time = int(now - start_time)

        next_fetch_time = self.start_time + (fetcher["interval"] * 60)

        data = {
            "$inc": {
                "succ": succ,
                "fail": fail,
                "skip": skip,
                "total": total,
            },
            "$set": {
                "next_fetch_time": next_fetch_time,
            }
        }

        ProxyManager.proxy_manager.updateFetcher(name, data)
        log.info("fetch [{name:^15}] proxy finish, \
            total:{total}, succ:{succ}, fail:{fail}, skip:{skip}, elapsed_time:{elapsed_time}s". \
            format(name=name, total=total, succ=succ, fail=fail, skip=skip, elapsed_time=elapsed_time))

    def run(self):
        while self.queue.qsize():
            self.fetch()


    
if __name__ == "__main__":
    ProxyFetch.initQueue()
    t = ProxyFetch()
    t.start()