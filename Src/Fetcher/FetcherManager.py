import sys
sys.path.append("Src")
import os
import importlib

from Config import ConfigManager

SKIP_FILE_LIST = [
    "__init__.py",
    "__pycache__",
]

fetcher_list = []

def init():
    file_names = os.listdir("Src/Fetcher/fetchers")
    for file_name in file_names:
        if file_name in SKIP_FILE_LIST:
            pass
        else:
            name = os.path.splitext(file_name)[0]
            fetcher_class = get_class(name)
            fetcher_name = fetcher_class.fetcher_name
            fetcher_list.append(fetcher_name)
    
    ConfigManager.fetcher_config.update_fetcher_list(fetcher_list)

    return True

def get_class(name):
    module_name = "Fetcher.fetchers.%s" % (name)
    module = importlib.import_module(module_name)
    result = getattr(module, name)
    return result

init()

if __name__ == '__main__':
    print("fetcher_list: ", bool(fetcher_list))

    class_name = "Fetcher1"
    print("get_class: ", get_class(class_name).fetcher_name == class_name)