import sys
sys.path.append("Src")

from pymongo import MongoClient
from Config import ConfigManager

import importlib

mc = MongoClient(ConfigManager.base_config.setting.get("db_host"), ConfigManager.base_config.setting.get("db_port"))

VERSION_FILE_PATH = "version"
version_list = []

def init():
    with open(VERSION_FILE_PATH) as f:
        items = f.readlines()
        for item in items:
            version_list.append(item.strip())

def get_last_version():
    result = version_list[0]
    return result

def update_version(cur_version):
    index = version_list.index(cur_version)
    while index:
        index = index - 1
        next_version = version_list[index]
        version_name = next_version.replace(".", "_")
        last_version = get_last_version()

        module_name = "version.version_{version_name}".format(version_name=version_name)

        try:
            module = importlib.import_module(module_name)
            result = module.run(mc, last_version, next_version, cur_version)
        except Exception:
            result = False

        query = {"setting_name": "version"}
        data = {
            "$set": {
                "setting_value": next_version
            }
        }
        mc.proxy.setting.update(query, data)

        cur_version = next_version

def run():
    item = mc.proxy.setting.find_one({"setting_name": "version"})
    if item:
        cur_version = item["setting_value"]
        update_version(cur_version)
    else:
        last_version = get_last_version()
        data = {
            "setting_name": "version",
            "setting_value": last_version,
            "setting_value": True,
        }
        mc.proxy.setting.insert(data)


    mc.close()

if __name__ == '__main__':
    init()
    run()