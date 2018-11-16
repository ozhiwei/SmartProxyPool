# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading

from apscheduler.schedulers.background import BackgroundScheduler as Sch
from Manager.ProxyFetch import ProxyFetch

from Log.LogManager import log
from Config.ConfigManager import config

def fetch_new_proxy():
    ProxyFetch.initQueue()
    for _ in range(config.BASE.fetch_new_proxy_thread):
        pf = ProxyFetch()
        pf.daemon = True
        pf.start()


def run():
    sch = Sch()
    sch.add_job(fetch_new_proxy, 'interval', minutes=config.BASE.fetch_new_proxy_interval)
    sch.start()

    fetch_new_proxy()

    while 1:
        pass

if __name__ == '__main__':
    run()
