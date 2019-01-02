# -*- coding: utf-8 -*-

import sys
sys.path.append("Src")

import time
from threading import Thread

from Log import LogManager
from Web.app import run as proxy_web_run
from Schedule.ProxyVerifySchedule import ProxyVerifySchedule
from Schedule.ProxyFetchSchedule import ProxyFetchSchedule
from Schedule.ProxyCleanSchedule import ProxyCleanSchedule

TASK_LIST = {
    "ProxyVerifySchedule": ProxyVerifySchedule,
    "ProxyFetchSchedule": ProxyFetchSchedule,
    "ProxyCleanSchedule": ProxyCleanSchedule
}

def show_time():
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    content = "{newline}{symbol} ProxyPool Start, date:{date} {symbol}{newline}".format(newline="\n", symbol="-"*50, date=date)
    print(content)

def start_thread_list():
    task_list = []
    for name in TASK_LIST.keys():
        sch = TASK_LIST[name]()
        t = Thread(target=sch.run, name=name)
        task_list.append(t)

    for t in task_list:    
        t.daemon = True
        t.start()

def main(test=False):
    show_time()
    LogManager.Init()
    start_thread_list()

    proxy_web_run()

if __name__ == '__main__':
    main()