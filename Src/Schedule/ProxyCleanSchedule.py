# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading

from apscheduler.schedulers.background import BackgroundScheduler as Sch
from Manager.ProxyClean import ProxyCleanRaw, ProxyCleanUseful
from Manager.ProxyFetch import ProxyFetch

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

from Manager.ProxyManager import ProxyManager
from Log.LogManager import log
from Config.ConfigManager import config

def clean_raw_proxy():
    t = ProxyCleanRaw()
    t.daemon = True
    t.start()


def clean_useful_proxy():
    t = ProxyCleanUseful()
    t.daemon = True
    t.start()

def run():
    sch = Sch()
    sch.add_job(clean_raw_proxy, "interval", minutes=config.BASE.clean_raw_proxy_interval)
    sch.add_job(clean_useful_proxy, "interval", minutes=config.BASE.clean_useful_proxy_interval)
    sch.start()

    clean_raw_proxy()
    clean_useful_proxy()

    while 1:
        pass

if __name__ == '__main__':
    run()
