# -*- coding: utf-8 -*-
# !/usr/bin/env python

# base import
import sys
sys.path.append("Src")

# framework import
import flask_restful 
from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource

# project import
from Config.ConfigManager import config
from Manager.ProxyManager import proxy_manager

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('https', type=bool, default=0, choices=[0,1], location='args')
parser.add_argument('token', type=str, location='args')


@app.errorhandler(404)
def miss(e):
    data = {
        "result": "not found",
        "status_code": 404,
        "github": "https://github.com/1again/ProxyPool",
        "href": ["/v1/"],
    }
    result = jsonify(data)
    return result, 404

API_LIST = {
    "/v1/proxy/": {
        "args": {
            "https": {
                "value": [0,1],
                "desc": "need https proxy? 1 true and 0 false"
            },
            "token": {
                "value": "random string + random number",
                "desc": "Avoid Get Repetition Proxy",
            },
        },
        "desc": "Get A Random Proxy"
    },
    "/v1/proxys/": {
        "desc": "Get All Proxy",
    }
}

class ApiList(Resource):
    def get(self):
        result = jsonify(API_LIST)

        return result

class Proxy(Resource):
    def get(self):
        args = parser.parse_args()

        result = {}

        options = {
            "https": bool(args.get('https')),
            "token": args.get('token'),
        }

        if options.get("token", None):
            result["result"] = proxy_manager.getQualityProxy(**options)
        else:
            result["result"] = proxy_manager.getSampleProxy(**options)

        return result

class Proxys(Resource):
    def get(self):
        result = {}
        result["result"] = proxy_manager.getAll()

        return result

api.add_resource(Proxys, '/v1/proxys/')
api.add_resource(Proxy, '/v1/proxy/')
api.add_resource(ApiList, '/v1/')


def run():
    if sys.platform.startswith("win"):
        app.run(host=config.API.bind_ip, port=config.API.bind_port)
    else:
        app.run(host=config.API.bind_ip, port=config.API.bind_port, threaded=False, processes=config.API.processes)


if __name__ == '__main__':
    run()