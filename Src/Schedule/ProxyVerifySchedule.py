# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading

from apscheduler.schedulers.background import BackgroundScheduler as Sch
from Manager.ProxyVerify import ProxyVerifyRaw, ProxyVerifyUseful
from Manager.ProxyFetch import ProxyFetch

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

from Manager.ProxyManager import ProxyManager
from Log.LogManager import log
from Config.ConfigManager import config

def verify_raw_proxy():
    ProxyVerifyRaw.initQueue()
    for _ in range(config.BASE.verify_raw_proxy_thread):
        t = ProxyVerifyRaw()
        t.daemon = True
        t.start()


def verify_useful_proxy():
    ProxyVerifyUseful.initQueue()
    for _ in range(config.BASE.verify_useful_proxy_thread):
        t = ProxyVerifyUseful()
        t.daemon = True
        t.start()

def run():
    sch = Sch()
    sch.add_job(verify_raw_proxy, "interval", minutes=config.BASE.verify_raw_proxy_interval)
    sch.start()

    verify_raw_proxy()
    verify_useful_proxy()

    while 1:
        pass

if __name__ == '__main__':
    run()
