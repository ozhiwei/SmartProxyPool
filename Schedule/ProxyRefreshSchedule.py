# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
import time
import threading

from apscheduler.schedulers.background import BackgroundScheduler as Sch

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.EnvUtil import PY3
from Log.LogManager import log

class ProxyRefreshSchedule(ProxyManager):

    def __init__(self):
        ProxyManager.__init__(self)

        self.remaining_proxies = self.getAll()

        self.queue = Queue()
        items = self.getAllRawProxy()
        for proxy in items.keys():
            self.queue.put(proxy) 

    def validProxy(self):

        thread_id = threading.currentThread().ident
        log.info("thread_id:{thread_id}, Start ValidProxy `raw_proxy_queue`".format(thread_id=thread_id))

        total = 0
        succ = 0
        fail = 0

        while self.queue.qsize():
            proxy = self.queue.get()
            if proxy not in self.remaining_proxies:
                (http_result, https_result) = validUsefulProxy(proxy)
                if http_result:
                    self.saveUsefulProxy(proxy, https_result)
                    self.deleteRawProxy(proxy)
                    self.remaining_proxies.append(proxy)

                    succ = succ + 1
                else:
                    self.tickRawProxyVaildFail(proxy)

                    fail = fail + 1
                    log.debug('ProxyRefreshSchedule: %s validation fail' % proxy)
                # self.tickRawProxyVaildSucc(proxy)
                log.debug('ProxyRefreshSchedule: %s validation pass' % proxy)
            else:
                self.deleteRawProxy(proxy)

                log.debug('ProxyRefreshSchedule: %s repetition, skip!' % proxy)

            self.queue.task_done()
            self.tickRawProxyVaildTotal(proxy)
            total = total + 1

        log.info('thread_id:{thread_id}, ValidProxy Complete `raw_proxy_queue`, total:{total}, succ:{succ}, fail:{fail}'.format(thread_id=thread_id, total=total, succ=succ, fail=fail))

def refreshPool():
    pp = ProxyRefreshSchedule()
    pp.validProxy()


def batch_refresh(process_num=10):
    pp = ProxyRefreshSchedule()

    pl = []
    for num in range(process_num):
        proc = threading.Thread(target=pp.validProxy, args=())
        pl.append(proc)

    for num in range(process_num):
        pl[num].daemon = True
        pl[num].start()

def fetch_all():
    p = ProxyRefreshSchedule()
    p.refresh()


def run():
    sch = Sch()
    sch.add_job(fetch_all, 'interval', minutes=5)  # 每5分钟抓取一次
    sch.add_job(batch_refresh, "interval", minutes=5)  # 每分钟检查一次
    sch.start()

    fetch_all()
    batch_refresh()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    run()
