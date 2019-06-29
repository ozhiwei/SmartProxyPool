# -*- coding: utf-8 -*-
# !/usr/bin/env python

from gevent import monkey
monkey.patch_all()

import sys
sys.path.append("Src")
import time
import threading
import datetime

from Manager.ProxyFetch import ProxyFetch
from Manager import ProxyManager
from Schedule.ProxySchedule import ProxySchedule

from Log.LogManager import log
from Config import ConfigManager

class ProxyFetchSchedule(ProxySchedule):

    def __init__(self, **kwargs):
        super(ProxyFetchSchedule, self).__init__(**kwargs)
        self.task_handler_hash = {
            "fetch_new_proxy_interval": self.fetchNewProxy,
        }

    def checkFetchNewProxy(self):

        total_number = ProxyManager.proxy_manager.getUsefulProxyNumber()
        hold_number = ConfigManager.setting_config.setting.get("hold_useful_proxy_number")
        if total_number < hold_number or hold_number == -1:
            log.debug("fetch new proxy start, exist raw_proxy total_number:{total_number}, hold_number:{hold_number}".format(total_number=total_number, hold_number=hold_number))
            result = True
        else:
            log.debug("fetch new proxy skip, exist raw_proxy total_number:{total_number}, hold_number:{hold_number}".format(total_number=total_number, hold_number=hold_number))
            result = False
        
        return result

    def fetchNewProxy(self):
        if self.checkFetchNewProxy():
            ProxyFetch.initQueue()
            t = ProxyFetch()
            t.start()

if __name__ == '__main__':
    sch = ProxyFetchSchedule()
    sch.run()
