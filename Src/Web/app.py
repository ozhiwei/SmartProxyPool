# -*- coding: utf-8 -*-
# !/usr/bin/env python

# base import
import time
import math
import os
import sys
sys.path.append("Src/")
sys.path.insert(0, "Src/Web/packages/")
sys.path.insert(0, "Src/Web/packages/flask-security/")

from flask import Flask

from Config.ConfigManager import config

app = Flask(__name__)

def init_app():
    app.config.from_pyfile('config.py')
    app.config["MONGODB_SETTINGS"] = {
        'db': config.setting.DB.name,
        'host': config.setting.DB.host,
        'port': config.setting.DB.port,
        'username': config.setting.DB.username,
        'password': config.setting.DB.password,
    }

def run():
    init_app()

    from Web.admin import admin
    from Web.api import api

    admin.init_app(app)
    api.init_app(app)

    app.run(host=config.setting.Other.bind_ip, port=config.setting.Other.bind_port, threaded=False)

if __name__ == '__main__':
    run()