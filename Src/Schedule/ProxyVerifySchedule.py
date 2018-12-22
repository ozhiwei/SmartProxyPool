# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading

from Manager.ProxyVerify import ProxyVerifyRaw, ProxyVerifyUseful
from Manager.ProxyFetch import ProxyFetch
from Notify.NotifyManager import register_notify
from Schedule.ProxySchedule import ProxySchedule

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

from Manager.ProxyManager import ProxyManager
from Log.LogManager import log
from Config.ConfigManager import config

class ProxyVerifySchedule(ProxySchedule):

    def __init__(self, **kwargs):
        super(ProxyVerifySchedule, self).__init__(**kwargs)
        self.task_handler_hash = {
            "verify_raw_proxy_interval": self.verify_raw_proxy,
            "verify_useful_proxy_interval": self.verify_useful_proxy,
        }

    def verify_raw_proxy(self):
        thread_list = []
        ProxyVerifyRaw.initQueue()
        for _ in range(config.setting.Thread.verify_raw_proxy_thread):
            t = ProxyVerifyRaw()
            t.daemon = True
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()

    def verify_useful_proxy(self):
        thread_list = []
        ProxyVerifyUseful.initQueue()
        for _ in range(config.setting.Thread.verify_useful_proxy_thread):
            t = ProxyVerifyUseful()
            t.daemon = True
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()

if __name__ == '__main__':
    sch = ProxyVerifySchedule()
    sch.run()
