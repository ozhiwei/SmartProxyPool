# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")

import threading
import requests
import re
import time

from Manager.ProxyManager import ProxyManager
from Log.LogManager import log
from Util.GetConfig import config

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2


PROXY_TYPE = {
    "CLEAR": 1,
    "COMMON_ANONYMOUS": 2,
    "HIGH_ANONYMOUS": 3,
}

class ProxyResult(object):
    pass

class ProxyVerify(threading.Thread):
    def __init__(self, **kwargs):
        super(ProxyVerify, self).__init__(**kwargs)
        self.proxy_manager = ProxyManager()
    
    # TODO: 逻辑应该有问题, 但不确定
    # http是可用的才会保存https, 会不会有只开通https的代理呢?
    def verifyProxy(self, proxy):
        result = ProxyResult()

        if isinstance(proxy, bytes):
            proxy = proxy.decode('utf8')

        data = proxy.split(':')
        result.ip = data[0]
        result.port = data[1]
        result.address = proxy
        

        proxies = {
            "http": proxy,
            "https": proxy,
        }
        http_url = "http://httpbin.org/ip"
        https_url = "https://httpbin.org/ip"

        result.http = False
        result.https = False

        # http verify
        try:
            r = requests.get(http_url, proxies=proxies, timeout=10, verify=False)
            data = r.json()
            ip_string = data["origin"]
            ip_list = ip_string.split(", ")

            status_result = r.status_code == 200
            content_result = result.ip in ip_list
            if status_result and content_result:
                result.http = True

            if len(ip_list) > 1:
                result.type = PROXY_TYPE["CLEAR"]
            else:
                result.type = PROXY_TYPE["COMMON_ANONYMOUS"]

        except Exception as e:
            log.debug("proxy:{proxy} http verify proxy fail, error:{error}".format(proxy=proxy, error=e))
            result.http = False

        if result.http:

            # https verify
            try:
                r = requests.get(https_url, proxies=proxies, timeout=10, verify=False)
                data = r.json()
                ip_string = data["origin"]
                ip_list = ip_string.split(", ")

                status_right = r.status_code == 200
                content_right = result.ip in ip_list
                if status_right and content_right:
                    result.https = True

            except Exception as e:
                log.debug("proxy:{proxy} https verify proxy fail, error:{error}".format(proxy=proxy, error=e))
                result.https = False

        return result

# 这样的实现多线程有问题, 后期无法扩展到独立的机器上.
# must call classmethod initQueue before
class ProxyVerifyRaw(ProxyVerify):
    queue = Queue()
    useful_proxys = {}

    def __init__(self, **kwargs):
        super(ProxyVerifyRaw, self).__init__(**kwargs)

    @classmethod
    def initQueue(cls):
        proxy_manager = ProxyManager()
        proxies = proxy_manager.getAllRawProxy()
        for proxy in proxies:
            cls.queue.put(proxy)

        cls.useful_proxys = proxy_manager.getAllProxy()

    def run(self):

        start_time = time.time()
        thread_id = threading.currentThread().ident
        log.debug("thread_id:{thread_id}, raw_proxy proxy verify start".format(thread_id=thread_id))

        total = 0
        succ = 0
        fail = 0
        skip = 0

        while self.queue.qsize():
            raw_proxy_item = self.queue.get()
            raw_proxy = raw_proxy_item.get("proxy")
            if isinstance(raw_proxy, bytes):
                raw_proxy = raw_proxy.decode('utf8')

            if raw_proxy not in self.useful_proxys:
                proxy = self.verifyProxy(raw_proxy)
                if proxy.http:
                    self.proxy_manager.saveUsefulProxy(proxy)
                    self.proxy_manager.deleteRawProxy(raw_proxy)
                    self.useful_proxys[raw_proxy] = True

                    succ = succ + 1
                    log.debug("raw_proxy:{raw_proxy} verify succ".format(raw_proxy=raw_proxy))
                else:
                    self.proxy_manager.tickRawProxyVaildFail(raw_proxy)

                    fail = fail + 1
                    log.debug("raw_proxy:{raw_proxy} verify fail".format(raw_proxy=raw_proxy))
            else:
                self.proxy_manager.deleteRawProxy(raw_proxy)

                skip = skip + 1
                log.debug("raw_proxy:{raw_proxy} verify repetition".format(raw_proxy=raw_proxy))

            self.queue.task_done()

            self.proxy_manager.tickRawProxyVaildTotal(raw_proxy)
            total = total + 1

        end_time = time.time()
        elapsed_time = int(end_time - start_time)
        log.info("thread_id:{thread_id}, raw_proxy verify  proxy finish, total:{total}, succ:{succ}, fail:{fail}, skip:{skip}, elapsed_time:{elapsed_time}s".format(thread_id=thread_id, total=total, succ=succ, fail=fail, skip=skip, elapsed_time=elapsed_time))

# 这样的实现多线程有问题, 后期无法扩展到独立的机器上.
# must call classmethod initQueue before
class ProxyVerifyUseful(ProxyVerify):
    queue = Queue()

    def __init__(self, **kwargs):
        super(ProxyVerifyUseful, self).__init__(**kwargs)

    @classmethod
    def initQueue(cls):
        proxy_manager = ProxyManager()
        proxies = proxy_manager.getAllProxy()
        for proxy in proxies:
            cls.queue.put(proxy)

    def run(self):

        start_time = time.time()
        thread_id = threading.currentThread().ident
        log.debug("thread_id:{thread_id} useful_proxy proxy verify start".format(thread_id=thread_id))

        total = 0
        succ = 0
        fail = 0
        while self.queue.qsize():
            proxy_item = self.queue.get()
            proxy = proxy_item.get("proxy")
            result = self.verifyProxy(proxy)
            if result.http:
                self.proxy_manager.tickUsefulProxyVaildSucc(proxy)
                succ = succ + 1
                log.debug("useful_proxy:{proxy} verify succ".format(proxy=proxy))
            else:
                self.proxy_manager.tickUsefulProxyVaildFail(proxy)
                fail = fail + 1
                log.debug("useful_proxy:{proxy} verify fail".format(proxy=proxy))

            self.queue.task_done()
            self.proxy_manager.tickUsefulProxyVaildTotal(proxy)
            total = total + 1
        
        end_time = time.time()
        elapsed_time = int(end_time - start_time)
        log.info('thread_id:{thread_id} useful_proxy verify proxy finish, total:{total}, succ:{succ}, fail:{fail}, elapsed_time:{elapsed_time}s'.format(thread_id=thread_id, total=total, succ=succ, fail=fail, elapsed_time=elapsed_time))

if __name__ == "__main__":
    t_list = []
    ProxyVerifyRaw.initQueue()
    for _ in range(10):
        t = ProxyVerifyRaw()
        t_list.append(t)

    ProxyVerifyUseful.initQueue()
    for _ in range(10):
        t = ProxyVerifyUseful()
        t_list.append(t)

    for t in t_list:
        t.daemon = True
        t.start()

    for t in t_list:
        t.join()