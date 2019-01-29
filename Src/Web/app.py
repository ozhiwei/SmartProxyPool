# -*- coding: utf-8 -*-
# !/usr/bin/env python

# base import
from gevent import monkey
monkey.patch_all()

import time
import math
import os
import sys
sys.path.append("Src/")

import logging
from flask import Flask
from  gevent.pywsgi import WSGIServer
from Config.ConfigManager import config

ACCESS_LOG_PATH = "logs/app_access.log"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


logger = logging.getLogger() 
def init_log():
    file_handler = logging.FileHandler(ACCESS_LOG_PATH)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

    return logger

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

    http_server = WSGIServer((config.setting.Other.bind_ip, config.setting.Other.bind_port), app, log=logger, error_log=logger)
    http_server.serve_forever()

def run():
    init_app()
    start_app()


if __name__ == '__main__':
    run()