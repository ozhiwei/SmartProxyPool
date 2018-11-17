# -*- coding: utf-8 -*-

import sys
sys.path.append('.')
sys.path.append('Src')

import time
from multiprocessing import Process

from Log import LogManager
from Api.ProxyApi import run as ProxyApiRun
from Schedule.ProxyVerifySchedule import run as VerifyRun
from Schedule.ProxyFetchSchedule import run as FetchRun
from Schedule.ProxyCleanSchedule import run as ProxyCleanRun

def showTime():
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    content = "{newline}{symbol} ProxyPool Start, date:{date} {symbol}{newline}".format(newline="\n", symbol="-"*50, date=date)
    print(content)

def main(test=False):
    showTime()
    LogManager.Init()

    process_hash = {
        "ProxyApiRun": ProxyApiRun,
        "VerifyRun": VerifyRun,
        "FetchRun": FetchRun,
        "ProxyClean": ProxyCleanRun
    }

    for name in process_hash.keys():
        p = Process(target=process_hash[name], name=name)
        p.daemon = True
        p.start()

    if test:
        time.sleep(5)
        sys.exit(0)
    else:
        while 1:
            pass

if __name__ == '__main__':
    main()