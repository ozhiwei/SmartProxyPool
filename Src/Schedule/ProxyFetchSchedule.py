# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
sys.path.append("Src")
import time
import threading
import datetime

from Manager.ProxyFetch import ProxyFetch
from Manager.ProxyManager import ProxyManager
from Schedule.ProxySchedule import ProxySchedule

from Log.LogManager import log
from Notify.NotifyManager import register_notify
from Config.ConfigManager import config

class ProxyFetchSchedule(ProxySchedule):

    def __init__(self, **kwargs):
        super(ProxyFetchSchedule, self).__init__(**kwargs)
        self.task_handler_hash = {
            "fetch_new_proxy_interval": self.fetch_new_proxy,
        }

    def fetch_new_proxy(self):
        proxy_manager = ProxyManager()
        total_number = proxy_manager.getRawProxyNumber()
        hold_number = config.setting.Hold.hold_raw_proxy_number
        if total_number < hold_number or hold_number == -1:
            log.debug("fetch new proxy start, exist raw_proxy total_number:{total_number}, hold_number:{hold_number}".format(total_number=total_number, hold_number=hold_number))

            ProxyFetch.initQueue()
            for _ in range(config.setting.Thread.fetch_new_proxy_thread):
                pf = ProxyFetch()
                pf.daemon = True
                pf.start()
        else:
            log.info("fetch new proxy skip, exist raw_proxy total_number:{total_number}, hold_number:{hold_number}".format(total_number=total_number, hold_number=hold_number))

if __name__ == '__main__':
    sch = ProxyFetchSchedule()
    sch.run()
