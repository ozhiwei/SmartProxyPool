# -*- coding: utf-8 -*-
# !/usr/bin/env python

from gevent import monkey
monkey.patch_all()

import sys
sys.path.append("Src")

import threading
import requests
import re
import time
import gevent

from Manager import ProxyManager
from Log.LogManager import log
from Config import ConfigManager

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

class Info(object):
    pass

class ProxyVerify(object):

    # http可用才会检查https, 会不会有只开通https的代理呢?
    def getProxyInfo(self, proxy):
        info = Info()

        data = proxy.split(':')
        info.ip = data[0]
        info.port = data[1]
        info.address = proxy

        proxies = {
            "http": proxy,
            "https": proxy,
        }
        http_url = "http://httpbin.org/ip"
        https_url = "https://httpbin.org/ip"

        result = False

        info.https = ProxyManager.PROXY_HTTPS["UNKNOWN"]
        info.type = ProxyManager.PROXY_TYPE["UNKNOWN"]
        # http verify
        try:
            r = requests.get(http_url, proxies=proxies, timeout=10, verify=False)
            data = r.json()
            ip_string = data["origin"]
            ip_list = ip_string.split(", ")

            status_result = r.status_code == 200
            content_result = "origin" in data
            if status_result and content_result:
                result = True

            if len(ip_list) > 1:
                info.type = ProxyManager.PROXY_TYPE["CLEAR"]
            else:
                info.type = ProxyManager.PROXY_TYPE["ANONYMOUS"]

        except Exception as e:
            log.debug("proxy:{proxy} http verify proxy fail, error:{error}".format(proxy=proxy, error=e))
            result = False

        if result:

            # https verify
            try:
                r = requests.get(https_url, proxies=proxies, timeout=10, verify=False)
                status_result = r.status_code == 200
                content_result = "origin" in data
                if status_result and content_result:
                    info.https = ProxyManager.PROXY_HTTPS["ENABLE"]

            except Exception as e:
                log.debug("proxy [{proxy}] https verify fail, error:{error}".format(proxy=proxy, error=e))
                info.https = ProxyManager.PROXY_HTTPS["DISABLE"]

        return info

    def defaultVerifyProxy(self, proxy):
        result = None

        if isinstance(proxy, bytes):
            proxy = proxy.decode('utf8')

        proxies = {
            "http": proxy,
        }
        http_url = "http://httpbin.org/ip"

        try:
            r = requests.get(http_url, proxies=proxies, timeout=10, verify=False)
            data = r.json()

            status_result = r.status_code == 200
            content_result = "origin" in data
            if status_result and content_result:
                result = True

        except Exception as e:
            log.debug("proxy:{proxy} http verify proxy fail, error:{error}".format(proxy=proxy, error=e))
            result = False

        return result

    def customVerifyProxy(self, proxy):
        result = None

        if isinstance(proxy, bytes):
            proxy = proxy.decode('utf8')

        proxies = {
            "http": proxy,
            "https": proxy,
        }
        verify_url = ConfigManager.setting_config.setting.get("custom_verify_url")

        try:
            content_result = True
            r = requests.get(verify_url, proxies=proxies, timeout=10, verify=False)
            pattern = ConfigManager.setting_config.setting.get("custom_verify_content")
            if pattern:
                content = r.content.decode('utf-8')
                search_result = re.search(pattern, content)
                content_result = search_result != None

            status_result = r.status_code == 200
            if status_result and content_result:
                result = True

        except Exception as e:
            log.debug("proxy:{proxy} http verify proxy fail, error:{error}".format(proxy=proxy, error=e))
            result = False

        return result

    def verify(self):
        pass

    def run(self):
        while self.queue.qsize():
            self.verify()

# 这样的实现多线程有问题, 后期无法扩展到独立的机器上.
# must call classmethod initQueue before
class ProxyVerifyRaw(ProxyVerify):
    queue = Queue()
    useful_proxies = {}

    @classmethod
    def initQueue(cls):
        items = ProxyManager.proxy_manager.getAllRawProxy()
        for item in items:
            cls.queue.put(item)

        items = ProxyManager.proxy_manager.getAllUsefulProxy()
        data = { item["proxy"]: 1 for item in items }
        cls.useful_proxies = data

    def verify(self):
        raw_proxy_item = self.queue.get()
        raw_proxy = raw_proxy_item.get("proxy")
        if isinstance(raw_proxy, bytes):
            raw_proxy = raw_proxy.decode('utf8')

        if raw_proxy not in self.useful_proxies:
            if ConfigManager.setting_config.setting.get("custom_verify_url"):
                verify_result = self.customVerifyProxy(raw_proxy)
            else:
                verify_result = self.defaultVerifyProxy(raw_proxy)                    
            
            if verify_result:
                ProxyManager.proxy_manager.saveUsefulProxy(raw_proxy)
                ProxyManager.proxy_manager.deleteRawProxy(raw_proxy)
                self.useful_proxies[raw_proxy] = True

                self.stat["succ"] = self.stat["succ"] + 1
                log.debug("raw_proxy:{raw_proxy} verify succ".format(raw_proxy=raw_proxy))
            else:
                ProxyManager.proxy_manager.tickRawProxyVaildFail(raw_proxy)

                self.stat["fail"] = self.stat["fail"] + 1
                log.debug("raw_proxy:{raw_proxy} verify fail".format(raw_proxy=raw_proxy))
        else:
            ProxyManager.proxy_manager.deleteRawProxy(raw_proxy)

            self.stat["skip"] = self.stat["skip"] + 1
            log.debug("raw_proxy:{raw_proxy} verify repetition".format(raw_proxy=raw_proxy))

        self.queue.task_done()
        self.stat["total"] = self.stat["total"] + 1

    def start(self):

        start_time = time.time()
        log.debug("raw_proxy proxy verify start")

        self.stat = dict(
            total = 0,
            succ = 0,
            fail = 0,
            skip = 0,
        )

        concurrency = ConfigManager.setting_config.setting.get("verify_raw_proxy_concurrency")
        queue_size = self.queue.qsize()
        if concurrency > queue_size:
            spawn_num = queue_size
        else:
            spawn_num = concurrency

        greenlet_list = []
        for _ in range(spawn_num):
            greenlet_list.append(gevent.spawn(self.run))

        gevent.joinall(greenlet_list)

        end_time = time.time()
        elapsed_time = int(end_time - start_time)
        log.info("raw_proxy verify  proxy finish, total:{total}, succ:{succ}, fail:{fail}, skip:{skip}, elapsed_time:{elapsed_time}s".format(total=self.stat["total"], succ=self.stat["succ"], fail=self.stat["fail"], skip=self.stat["skip"], elapsed_time=elapsed_time))

# 这样的实现多线程有问题, 后期无法扩展到独立的机器上.
# must call classmethod initQueue before
class ProxyVerifyUseful(ProxyVerify):
    queue = Queue()

    @classmethod
    def initQueue(cls):
        proxies = ProxyManager.proxy_manager.getAllUsefulProxy()
        for proxy in proxies:
            cls.queue.put(proxy)

    def checkProxyInfo(self, item):
        result = False
        if item.get("type") == ProxyManager.PROXY_TYPE["UNKNOWN"] or item.get("type") == None:
            result = True

        if item.get("https") == ProxyManager.PROXY_HTTPS["UNKNOWN"] or item.get("https") == None:
            result = True

        return result

    def updateUsefulProxy(self, item):
        proxy = item.get("proxy")
        info = self.getProxyInfo(proxy)
        ProxyManager.proxy_manager.updateUsefulProxy(item, info)

    def verify(self):
        item = self.queue.get()
        proxy = item.get("proxy")

        if ConfigManager.setting_config.setting.get("custom_verify_url"):
            verify_result = self.customVerifyProxy(proxy)
        else:
            verify_result = self.defaultVerifyProxy(proxy)

        if verify_result:
            if self.checkProxyInfo(item):
                self.updateUsefulProxy(item)

            ProxyManager.proxy_manager.tickUsefulProxyVaildSucc(proxy)
            self.stat["succ"] = self.stat["succ"] + 1
            log.debug("useful_proxy:{proxy} verify succ".format(proxy=proxy))
        else:
            ProxyManager.proxy_manager.tickUsefulProxyVaildFail(proxy)
            self.stat["fail"] = self.stat["fail"] + 1
            log.debug("useful_proxy:{proxy} verify fail".format(proxy=proxy))

        self.queue.task_done()
        ProxyManager.proxy_manager.tickUsefulProxyVaildTotal(proxy)
        self.stat["total"] = self.stat["total"] + 1

    def start(self):

        start_time = time.time()
        log.debug("useful_proxy proxy verify start")

        self.stat = dict(
            total = 0,
            succ = 0,
            fail = 0,
        )

        concurrency = ConfigManager.setting_config.setting.get("verify_useful_proxy_concurrency")
        queue_size = self.queue.qsize()
        if concurrency > queue_size:
            spawn_num = queue_size
        else:
            spawn_num = concurrency

        greenlet_list = []
        for _ in range(spawn_num):
            greenlet_list.append(gevent.spawn(self.run))

        gevent.joinall(greenlet_list)

        end_time = time.time()
        elapsed_time = int(end_time - start_time)
        log.info('useful_proxy verify proxy finish, total:{total}, succ:{succ}, fail:{fail}, elapsed_time:{elapsed_time}s'.format(total=self.stat["total"], succ=self.stat["succ"], fail=self.stat["fail"], elapsed_time=elapsed_time))

if __name__ == "__main__":
    ProxyVerifyRaw.initQueue()
    t = ProxyVerifyRaw()
    t.start()

    ProxyVerifyUseful.initQueue()
    t = ProxyVerifyUseful()
    t.start()