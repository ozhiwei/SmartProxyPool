# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading

from Manager.ProxyManager import ProxyManager
from Log.LogManager import log
from Config.ConfigManager import config

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

# 这样的实现多线程有问题, 后期无法扩展到独立的机器上.
# must call classmethod initQueue before
class ProxyClean(threading.Thread):
    def __init__(self, **kwargs):
        super(ProxyClean, self).__init__(**kwargs)
        self.proxy_manager = ProxyManager()

class ProxyCleanUseful(ProxyClean):

    def run(self):
        total = config.BASE.useful_proxy_clean_total / 100
        disable_rate = config.BASE.useful_proxy_clean_disable_rate / 100
        result = self.proxy_manager.cleanUsefulProxy(total=total, disable_rate=disable_rate)

        log.info("clean useful_proxy, number:{number}".format(number=result))

class ProxyCleanRaw(ProxyClean):

    def run(self):
        total = config.BASE.raw_proxy_clean_total / 100
        disable_rate = config.BASE.raw_proxy_clean_disable_rate / 100
        result = self.proxy_manager.cleanRawProxy(total=total, disable_rate=disable_rate)

        log.info("clean raw_proxy, number:{number}".format(number=result))

if __name__ == "__main__":
    t1 = ProxyCleanUseful()
    t1.daemon = True
    t1.start()

    t2 = ProxyCleanRaw()
    t2.daemon = True
    t2.start()

    t1.join()
    t2.join()