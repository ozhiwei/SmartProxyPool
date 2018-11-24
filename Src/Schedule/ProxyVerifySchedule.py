# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading
import datetime

from apscheduler.schedulers.blocking import BlockingScheduler as Sch
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
    now = datetime.datetime.now()
    sch.add_job(verify_raw_proxy, "interval", minutes=config.BASE.verify_raw_proxy_interval, next_run_time=now)
    sch.add_job(verify_useful_proxy, "interval", minutes=config.BASE.verify_useful_proxy_interval, next_run_time=now)
    sch.start()

if __name__ == '__main__':
    run()
