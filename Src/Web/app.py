# -*- coding: utf-8 -*-
# !/usr/bin/env python

# base import
import time
import math
import os
import sys
sys.path.append("Src/")
# sys.path.insert(0, "Src/site-packages/")

import logging
from flask import Flask

from Config.ConfigManager import config

ACCESS_LOG_PATH = "logs/app_access.log"

app = Flask(__name__)

def init_log():
    logger = logging.getLogger() 
    file_handler = logging.FileHandler(ACCESS_LOG_PATH)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

def init_config():
    app.config.from_pyfile('config.py')
    app.config["MONGODB_SETTINGS"] = {
        'db': config.setting.DB.name,
        'host': config.setting.DB.host,
        'port': config.setting.DB.port,
        'username': config.setting.DB.username,
        'password': config.setting.DB.password,
    }

def init_app():
    init_config()
    init_log()

def start_app():
    from Web.admin import admin
    from Web.api import api

    admin.init_app(app)
    api.init_app(app)

    app.run(host=config.setting.Other.bind_ip, port=config.setting.Other.bind_port, threaded=False)

def run():
    init_app()
    start_app()


if __name__ == '__main__':
    run()