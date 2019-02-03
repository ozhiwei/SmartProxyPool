# -*- coding: utf-8 -*-
# !/usr/bin/env python
from gevent import monkey
monkey.patch_all()

import sys
sys.path.append("Src")
import time

from Manager.ProxyVerify import ProxyVerifyRaw, ProxyVerifyUseful
from Schedule.ProxySchedule import ProxySchedule

from Log.LogManager import log
from Config import ConfigManager

class ProxyVerifySchedule(ProxySchedule):
    rightnow = True

    def __init__(self, **kwargs):
        super(ProxyVerifySchedule, self).__init__(**kwargs)
        self.task_handler_hash = {
            "verify_raw_proxy_interval": self.verify_raw_proxy,
            "verify_useful_proxy_interval": self.verify_useful_proxy,
        }

    def verify_raw_proxy(self):
        ProxyVerifyRaw.initQueue()
        t = ProxyVerifyRaw()
        t.start()

    def verify_useful_proxy(self):
        ProxyVerifyUseful.initQueue()
        t = ProxyVerifyUseful()
        t.start()

if __name__ == '__main__':
    sch = ProxyVerifySchedule()
    sch.run()
