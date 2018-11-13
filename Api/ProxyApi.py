# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

from Util.GetConfig import config
from Manager.ProxyManager import ProxyManager

app = Flask(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = {
    'get': u'get an usable proxy',
    'get_all': u'get all proxy from proxy pool',
    'get_status': u'proxy statistics'
}


@app.route('/')
def index():
    return api_list


@app.route('/get/')
def get():
    result = "no proxy"
    usable_rate = request.args.get('usable_rate', 0)
    https = request.args.get('https', False)
    options = {
        "usable_rate": usable_rate,
        "https": bool(https),
    }
    proxy = ProxyManager().getSampleUsefulProxy(**options)
    if proxy:
        result = proxy

    return result

@app.route('/get_all/')
def getAll():
    proxies = ProxyManager().getAll()
    return proxies

@app.route('/get_status/')
def getStatus():
    result = ProxyManager().getProxyNumber()
    return result


def run():
    if sys.platform.startswith("win"):
        app.run(host=config.host_ip, port=config.host_port)
    else:
        app.run(host=config.host_ip, port=config.host_port, threaded=False, processes=config.processes)


if __name__ == '__main__':
    run()
