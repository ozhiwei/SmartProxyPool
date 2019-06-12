# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys, os
sys.path.append("Src")

from Util.utilClass import ConfigParse
from pymongo import MongoClient
from Notify.NotifyManager import register_event, NOTIFY_EVENT

def is_number(s):
    result = False
    try:
        float(s)
        result = True
    except ValueError:
        pass

    if not result:
        try:
            import unicodedata
            unicodedata.numeric(s)
            result = True
        except (TypeError, ValueError):
            pass

    return result

class BaseConfig(object):
    config_name = "Config.ini"
    config_dir = "../../Config/"

    def __init__(self):
        pwd = os.path.dirname(os.path.realpath(__file__))
        relative_path = "{pwd}/{config_dir}".format(pwd=pwd, config_dir=self.config_dir)
        self.config_dir = os.path.realpath(relative_path)
        self.setting = {}

        self.load_config()

    def load_config(self):
        self.config_path = os.path.join(self.config_dir, self.config_name)
        self.default_config_path = os.path.join(self.config_dir, "Config.ini.default")

        self.config = self.load_config_from_path()

        self.load_setting()

    def load_config_from_path(self):
        config = ConfigParse()
        if os.path.exists(self.config_path):
            config.read(self.config_path)
        else:
            config.read(self.default_config_path)

        return config

    def load_setting(self):
        for section in self.config.sections():
            for item  in self.config.items(section): 
                field = item[0] 
                value = int(item[1]) if is_number(item[1]) else item[1] 
                self.setting[field] = value

class DBConfig(object):
    db_name = "proxy"
    docs_name = "default"

    def __init__(self):
        client = MongoClient(host=base_config.setting.get("db_host"), port=base_config.setting.get("db_port"), username=base_config.setting.get("db_user"), password=base_config.setting.get("db_pass"))

        self.db = client[self.db_name]

class SettingConfig(DBConfig):
    db_name = "proxy"
    docs_name = "setting"
    default_config = dict(
        verify_useful_proxy_concurrency = 100,
        verify_useful_proxy_interval = 30, 

        fetch_new_proxy_concurrency = 100,
        fetch_new_proxy_interval = 30,

        # clean proxy when number is positive
        # disable clean proxy when number is -1
        hold_useful_proxy_number = -1,
    )

    def __init__(self):
        super(SettingConfig, self).__init__()

        self.setting = {}
        self.load_data_to_db()
        self.load_setting_from_db()

        register_event(NOTIFY_EVENT["AFTER_SETTING_CHANGE"], self.dispatch_event)

    def dispatch_event(self, **kwargs):
        self.reload_setting_from_db(**kwargs)

    def load_data_to_db(self):
        for field, value  in self.default_config.items():
            query = { "setting_name": field }
            if self.db[self.docs_name].find_one(query):
                pass
            else:
                data = dict(
                    setting_name = field,
                    setting_value = value,
                    setting_state = True,
                )

                self.db[self.docs_name].insert_one(data)

    def load_setting_from_db(self):
        self.reload_setting_from_db()

    def reload_setting_from_db(self, **kwargs):
        cursor = self.db.setting.find()
        for item in cursor:
            if item["setting_state"]:
                field = item["setting_name"]
                value = item["setting_value"] 
                value = int(value) if is_number(value) else value
                self.setting[field] = value
            else:
                field = item["setting_name"]
                self.setting[field] = None

class FetcherConfig(DBConfig):
    db_name = "proxy"
    docs_name = "fetchers"

    def __init__(self):
        super(FetcherConfig, self).__init__()

        self.fetcher_list = []
        cursor = self.db[self.docs_name].find()
        for item in cursor:
            if item["status"]:
                self.fetcher_list.append(item["name"])

    def update_fetcher_list(self, items):
        for item in items:
            query = { "name": item }
            if self.db[self.docs_name].find_one(query):
                pass
            else:
                data = dict(
                    name = item,
                    status = True,
                    succ=0,
                    fail=0,
                    skip=0,
                    total=0,
                )
                self.db[self.docs_name].insert_one(data)
                self.fetcher_list.append(item)

    def get_fetcher_list(self):
        result = self.fetcher_list
        return result

    def update_stat(self, name, stat):
        query = {
            "name": name,
        }

        data = {
            "$inc": {
                "succ": stat["succ"],
                "fail": stat["fail"],
                "skip": stat["skip"],
                "total": stat["total"],
            }
        }

        self.db[self.docs_name].update(query, data)

base_config = BaseConfig()
setting_config = SettingConfig()
# fetcher_config = FetcherConfig()

if __name__ == '__main__':
    pass