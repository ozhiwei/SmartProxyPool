# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading
import datetime

from Schedule.ProxySchedule import ProxySchedule
from Manager.ProxyClean import ProxyCleanRaw, ProxyCleanUseful

from Log.LogManager import log
from Config import ConfigManager

class ProxyCleanSchedule(ProxySchedule):

    def __init__(self, **kwargs):
        super(ProxyCleanSchedule, self).__init__(**kwargs)
        self.task_handler_hash = {
            "clean_raw_proxy_interval": self.clean_raw_proxy,
            "clean_useful_proxy_interval": self.clean_useful_proxy,
        }

    def clean_raw_proxy(self):
        t = ProxyCleanRaw()
        t.daemon = True
        t.start()
        t.join()

    def clean_useful_proxy(self):
        t = ProxyCleanUseful()
        t.daemon = True
        t.start()
        t.join()

if __name__ == '__main__':
    sch = ProxyCleanSchedule()
    sch.run()