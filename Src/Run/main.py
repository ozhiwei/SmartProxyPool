# -*- coding: utf-8 -*-

import sys
sys.path.append("Src")

import time
from multiprocessing import Process

from Log import LogManager
from Web.app import run as WebRun
from Schedule.ProxyVerifySchedule import run as VerifyRun
from Schedule.ProxyFetchSchedule import run as FetchRun
from Schedule.ProxyCleanSchedule import run as ProxyCleanRun

PROCESS_HASH = {
    "WebRun": WebRun,
    "VerifyRun": VerifyRun,
    "FetchRun": FetchRun,
    "ProxyClean": ProxyCleanRun
}

def showTime():
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    content = "{newline}{symbol} ProxyPool Start, date:{date} {symbol}{newline}".format(newline="\n", symbol="-"*50, date=date)
    print(content)

def main(test=False):
    showTime()
    LogManager.Init()



    process_list = []
    for name in PROCESS_HASH.keys():
        p = Process(target=PROCESS_HASH[name], name=name)
        process_list.append(p)

    for p in process_list:    
        p.daemon = True
        p.start()

    if test:
        time.sleep(10)
    else:
        for p in process_list:
            p.join()

if __name__ == '__main__':
    main()