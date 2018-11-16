# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys, os
sys.path.append(".")

from Util.utilClass import ConfigParse


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

class ProxyObject(object):
    def __getattr__(self, name):
        return None

class ProxyConfig(object):

    def __init__(self):
        super(ProxyConfig, self).__init__()

        pwd = os.path.split(os.path.realpath(__file__))[0]
        config_dir = os.path.split(pwd)[0]

        config_path = os.path.join(config_dir, 'Config.ini.default')
        config = ConfigParse()
        config.read(config_path)
        self.initConfig(config)
        self.cf = config

        config_path = os.path.join(config_dir, 'Config.ini')
        if os.path.isfile(config_path):
            config.read(config_path)
            self.initConfig(config)
            self.cf = config

    def __getattr__(self, name):
        result = ProxyObject()
        return result

    def initConfig(self, config):
        for section in config.sections():
            setattr(self, section, ProxyObject())
            for item  in config.items(section):
                c = getattr(self, section)
                field = item[0]
                value = int(item[1]) if is_number(item[1]) else item[1]
                setattr(c, field, value)

    def get_config(self, sector, item):
        value = None
        try:
            value = self.cf[sector][item]
        except KeyError:
            pass
        finally:
            return value

    def get_options(self, option):
        return self.cf.options(option)

    def get_items(self, section):
        return self.cf.items(section)

config = ProxyConfig()

if __name__ == '__main__':
    print(config.DB.type)
    print(config.DB.host)
    print(config.DB.name)
    print(config.DB.port)
    print(config.LOG.level)
