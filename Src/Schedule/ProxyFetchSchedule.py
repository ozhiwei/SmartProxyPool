# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading

from apscheduler.schedulers.background import BackgroundScheduler as Sch
from Manager.ProxyFetch import ProxyFetch
from Manager.ProxyManager import proxy_manager
from Log.LogManager import log

from Log.LogManager import log
from Config.ConfigManager import config

def fetch_new_proxy():
    number = proxy_manager.getRawProxyNumber()
    if number < config.BASE.max_raw_proxy_number:
        log.debug("fetch new proxy start, exist raw_proxy number:{number}".format(number=number))

        ProxyFetch.initQueue()
        for _ in range(config.BASE.fetch_new_proxy_thread):
            pf = ProxyFetch()
            pf.daemon = True
            pf.start()
    else:
        log.info("fetch new proxy skip, exist raw_proxy number:{number}".format(number=number))


def run():
    sch = Sch()
    sch.add_job(fetch_new_proxy, 'interval', minutes=config.BASE.fetch_new_proxy_interval)
    sch.start()

    fetch_new_proxy()

    while 1:
        pass

if __name__ == '__main__':
    run()
