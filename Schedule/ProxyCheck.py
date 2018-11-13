# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyCheck
   Description :   多线程验证useful_proxy
   Author :        J_hao
   date：          2017/9/26
-------------------------------------------------
   Change Activity:
                   2017/9/26: 多线程验证useful_proxy
-------------------------------------------------
"""
__author__ = 'J_hao'

import sys
import threading

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Log.LogManager import log

class ProxyCheck(ProxyManager, threading.Thread):
    def __init__(self, queue, item_dict):
        ProxyManager.__init__(self)
        threading.Thread.__init__(self)
        self.queue = queue
        self.item_dict = item_dict

    def run(self):
        self.db.changeTable(self.useful_proxy_queue)
        thread_id = threading.currentThread().ident
        log.info("thread_id:{thread_id} useful_proxy proxy check start".format(thread_id=thread_id))

        total = 0
        succ = 0
        fail = 0
        while self.queue.qsize():
            proxy = self.queue.get()
            (http_result, _) = validUsefulProxy(proxy)
            if http_result:
                self.tickUsefulProxyVaildSucc(proxy)
                succ = succ + 1
                log.debug("ProxyCheck: {proxy} validation pass".format(proxy=proxy))
            else:
                self.tickUsefulProxyVaildFail(proxy)
                fail = fail + 1
                log.debug("ProxyCheck: {proxy} validation fail".format(proxy=proxy))

            self.queue.task_done()
            total = total + 1
            self.tickUsefulProxyVaildTotal(proxy)
        
        log.info('thread_id:{thread_id} proxy check end, total:{total}, succ:{succ}, fail:{fail}'.format(thread_id=thread_id, total=total, succ=succ, fail=fail))


if __name__ == '__main__':
    # p = ProxyCheck()
    # p.run()
    pass
