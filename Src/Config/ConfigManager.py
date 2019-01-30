# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys, os
sys.path.append("Src")

from Util.utilClass import ConfigParse
from pymongo import MongoClient
from Notify.NotifyManager import register_event, NOTIFY_EVENT

from Fetcher import FetcherManager

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

class Config(object):
    config_dir = "../../Config/"
    config_name = ""

    def __init__(self):
        pwd = os.path.dirname(os.path.realpath(__file__))
        relative_path = "{pwd}/{config_dir}".format(pwd=pwd, config_dir=self.config_dir)
        self.config_dir = os.path.realpath(relative_path)
        self.setting = {}

        self.load_config()

    def load_config(self):
        config_path = os.path.join(self.config_dir, self.config_name)
        self.config = self.load_config_from_path(config_path)
        self.load_setting()

    def check_docs_exists(self, path):
        if os.path.exists(path):
            result = True
        else:
            result = False
        
        return result


    def load_config_from_path(self, config_path):
        if os.path.exists(config_path):
            config = ConfigParse()
            config.read(config_path)

        return config

    def load_setting(self): 
        for section in self.config.sections():
            for item  in self.config.items(section): 
                field = item[0] 
                value = int(item[1]) if is_number(item[1]) else item[1] 
                self.setting[field] = value

class BaseConfig(Config):
    config_name = "Config.ini"

class PPConfig(Config):
    config_name = "DBConfig.ini.default"
    db_name = "proxy"
    docs_name = "setting"

    def __init__(self):
        super(PPConfig, self).__init__()
        client = MongoClient(host=bconfig.setting.get("db_host"), port=bconfig.setting.get("db_port"), username=bconfig.setting.get("db_user"), password=bconfig.setting.get("db_pass"))

        self.db = client[self.db_name]

        if self.check_docs_exists():
            pass
        else:
            self.load_data_to_db()

        self.load_setting_from_db()
        register_event(NOTIFY_EVENT["AFTER_SETTING_CHANGE"], self.dispatch_event)

    def dispatch_event(self, **kwargs):
        self.reload_setting_from_db(**kwargs)

    def check_docs_exists(self):
        result = self.db[self.docs_name].count() != 0
        return result

    def load_data_to_db(self):
        for section in self.config.sections():
            for item  in self.config.items(section):
                field = item[0]
                value = item[1]

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

    def load_setting(self):
        pass

class FetcherConfig(object):
    db_name = "proxy"
    docs_name = "fetchers"

    def __init__(self):
        super(FetcherConfig, self).__init__()
        client = MongoClient(host=bconfig.setting.get("db_host"), port=bconfig.setting.get("db_port"), username=bconfig.setting.get("db_user"), password=bconfig.setting.get("db_pass"))

        self.db = client[self.db_name]

        self.load_data_to_db()

        self.fetchers = []
        cursor = self.db[self.docs_name].find()
        for item in cursor:
            if item["status"]:
                self.fetchers.append(item["name"])

    def load_data_to_db(self):
        items = FetcherManager.get_fetchers()
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

    def get_fetchers(self):
        result = self.fetchers
        return result

    def update_fetcher_stat(self, name, stat):
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

    def load_setting(self):
        pass

bconfig = BaseConfig()
ppconfig = PPConfig()
fconfig = FetcherConfig()

if __name__ == '__main__':
    print("BaseConig db_host: ", bconfig.setting.get("db_host"))
    print("PPconfig verify_raw_proxy_concurrency: ", ppconfig.setting.get("verify_raw_proxy_concurrency"))
    print("FetcherConfig fetchers: ", fconfig.get_fetchers())