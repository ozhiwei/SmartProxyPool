import sys
sys.path.append("Src")
import os
import importlib

from Config import ConfigManager
from Manager import ProxyManager

SKIP_FILE_LIST = [
    "__init__.py",
    "__pycache__",
]

def init():
    file_names = os.listdir("Src/Fetcher/fetchers")
    for file_name in file_names:
        if file_name in SKIP_FILE_LIST:
            pass
        else:
            fetcher_name = os.path.splitext(file_name)[0]
            fetcher_class = getFetcherClass(fetcher_name)
            fetcher_host = fetcher_class.fetcher_host

            item = ProxyManager.proxy_manager.getFetcher(fetcher_name)
            if item:
                pass
            else:
                saveDefaultFetcher(fetcher_name, fetcher_host)

    return True

def saveDefaultFetcher(name, host):
    data = dict(
        name = name,
        host = host,
        status = True,
        succ=0,
        fail=0,
        skip=0,
        total=0,
        interval=30,
        next_fetch_time=0,
    )
    ProxyManager.proxy_manager.updateFetcher(name, data)

def getFetcherClass(name):
    module_name = "Fetcher.fetchers.%s" % (name)
    module = importlib.import_module(module_name)
    result = getattr(module, "CustomFetcher")
    return result

init()

if __name__ == '__main__':
    pass