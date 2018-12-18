# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys, os
sys.path.append(".")
sys.path.append("Src")

from Util.utilClass import ConfigParse
from pymongo import MongoClient
from Notify.NotifyManager import register_notify


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

class SettingObject(object):
    def __getattr__(self, name):
        result = SectionObject()
        setattr(self, name, result)
        return result

class SectionObject(object):
    def __getattr__(self, name):
        return None

class BaseConfig(object):
    config_dir = "../../Config/"

    def __init__(self):
        pwd = os.path.dirname(os.path.realpath(__file__))
        relative_path = "{pwd}/{config_dir}".format(pwd=pwd, config_dir=self.config_dir)
        self.config_dir = os.path.realpath(relative_path)
        self.setting = SettingObject()

        self.LoadDefaultConfig()
        self.LoadCurrentConfig()

    def LoadDefaultConfig(self):
        config_path = os.path.join(self.config_dir, 'Config.ini.default')
        self.default_config = self.LoadConfigByPath(config_path)
        # self.InitConfig(self.default_config)

    def LoadCurrentConfig(self):
        config_path = os.path.join(self.config_dir, 'Config.ini')
        self.current_config = self.LoadConfigByPath(config_path)
        self.InitConfig(self.current_config)

    def LoadConfigByPath(self, config_path):
        if os.path.exists(config_path):
            config = ConfigParse()
            config.read(config_path)

        return config

    def InitConfig(self, config): 
        for section in config.sections():
            c = getattr(self.setting, section)
            for item  in config.items(section): 
                field = item[0] 
                value = int(item[1]) if is_number(item[1]) else item[1] 
                setattr(c, field, value) 

class ProxyPoolConfig(BaseConfig):
    db_name = "proxy"
    collection_name = "setting"

    def __init__(self):
        super(ProxyPoolConfig, self).__init__()
        client = MongoClient(host=self.setting.DB.host, port=self.setting.DB.port, username=self.setting.DB.username, password=self.setting.DB.password)

        self.db = client[self.db_name]

        self.InitConfigFromDB()
        register_notify("reload_config_from_db", self.ReloadConfigFromDB)

    def LoadDefaultConfigToDB(self):
        if self.db[self.collection_name].count() == 0:
            for section in self.default_config.sections():
                for item  in self.default_config.items(section):
                    field = item[0]
                    value = item[1]


                    data = { 
                        "setting_group": section,
                        "setting_name": field,
                        "setting_value": value,
                        "setting_state": True,
                    }

                    self.InsertDBSettingConfig(data)

    def InsertDBSettingConfig(self, data):
        self.db[self.collection_name].insert_one(data)

    def InitConfigFromDB(self):
        self.LoadDefaultConfigToDB()
        self.ReloadConfigFromDB()

    def ReloadConfigFromDB(self):
        cursor = self.db.setting.find()
        for item in cursor:
            if (item["setting_state"]):
                section = getattr(self.setting, item["setting_group"])
                field = item["setting_name"]
                value = item["setting_value"] 
                value = int(value) if is_number(value) else value
                setattr(section, field, value)

    def GetConfigGroupList(self, group_name):
        result = []
        cursor = self.db.setting.find({"setting_group": group_name})
        for item in cursor:
            result.append(item)

        return result


config = ProxyPoolConfig()

if __name__ == '__main__':
    print(config.setting.DB.host)
    print(config.setting.DB.username)
    print(config.setting.Interval.clean_raw_proxy_interval)
    print(config.setting.Thread.verify_raw_proxy_thread)
    print(config.GetConfigGroupList("ProxyFetch"))
