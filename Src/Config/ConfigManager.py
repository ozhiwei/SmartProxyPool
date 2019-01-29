# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys, os
sys.path.append(".")
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

    def check_config_exists(self, path):
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

class FConfig(BaseConfig):
    config_name = "Config.ini"

class DBConfig(BaseConfig):
    config_name = "DBConfig.ini.default"
    db_name = "proxy"
    docs_name = "setting"

    def __init__(self):
        super(DBConfig, self).__init__()
        client = MongoClient(host=fconfig.setting.get("db_host"), port=fconfig.setting.get("db_port"), username=fconfig.setting.get("db_user"), password=fconfig.setting.get("db_pass"))

        self.db = client[self.db_name]

        if self.check_setting_exists():
            pass
        else:
            self.load_config_to_db()

        self.load_setting_from_db()
        register_event(NOTIFY_EVENT["AFTER_SETTING_CHANGE"], self.dispatch_event)

    def dispatch_event(self, **kwargs):
        self.reload_setting_from_db(**kwargs)

    def check_setting_exists(self):
        result = self.db[self.docs_name].count() != 0
        return result

    def load_config_to_db(self):
        for section in self.config.sections():
            for item  in self.config.items(section):
                field = item[0]
                value = item[1]

                data = {
                    "setting_name": field,
                    "setting_value": value,
                    "setting_state": True,
                }

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

fconfig = FConfig()
dbconfig = DBConfig()

if __name__ == '__main__':
    print("Config.ini db_host: ", fconfig.setting.get("db_host"))
    print("DBConfig.ini.default verify_raw_proxy_concurrency: ", dbconfig.setting.get("verify_raw_proxy_concurrency"))
