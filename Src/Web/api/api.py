from flask import Flask, jsonify, url_for, redirect, render_template, request
from flask_restful import reqparse, abort, Api, Resource

from Manager.ProxyManager import proxy_manager

API_LIST = {
    "/api/v1/proxy/": {
        "args": {
            "token": {
                "value": "random string + random number",
                "desc": "Avoid Get Repetition Proxy",
                "required": False,
            },
            "https": {
                "value": [1],
                "desc": "need https proxy? 1 == true",
                "required": False,
            },
            "region": {
                "value": "region name like 中国 or 广州 or 江苏",
                "desc": "Get Region Proxy",
                "required": False,
            },
            "type": {
                "value": [1,2],
                "desc": "clear proxy 1 or (common) anonymous 2",
                "required": False,
            }
        },
        "desc": "Get A Random Proxy"
    },
    "/api/v1/proxies/": {
        "args": {
            "https": {
                "value": [1],
                "desc": "need https proxy? 1 == true",
                "required": False,
            },
            "region": {
                "value": "region name like 中国 or 广州 or 江苏",
                "desc": "Get Region Proxy",
                "required": False,
            },
            "type": {
                "value": [1,2],
                "desc": "clear proxy 1 or (common) anonymous 2",
                "required": False,
            }
        },
        "desc": "Get All Proxy",
    },
    "/api/v1/proxies/stat/": {
        "args": {},
        "desc": "Statistics All Vaild Proxies",
    }
}

class ApiList(Resource):
    def get(self):
        result = jsonify(API_LIST)

        return result

class Proxy(Resource):
    def __init__(self, **kwargs):
        super(Proxy, self).__init__(**kwargs)

        parser = reqparse.RequestParser()
        parser.add_argument('https', type=int, choices=[1], location='args')
        parser.add_argument('type', type=int, choices=[1,2], location='args')
        parser.add_argument('region', type=str, location='args')
        parser.add_argument('token', type=str, location='args')
        self.args = parser.parse_args()

    def get(self):
        result = {
            "data": {}
        }
        data = {}

        options = {
            "https": bool(self.args.get('https')),
            "token": self.args.get('token'),
            "proxy_type": self.args.get('type'),
            "proxy_region": self.args.get('region'),
        }

        if options.get("token", None):
            data = proxy_manager.getQualityProxy(**options)
        else:
            data = proxy_manager.getSampleProxy(**options)
        
        if data:
            del data["_id"]

        if "used_token_list" in data:
            del data["used_token_list"]

        result["data"] = data

        return result


class Proxies(Resource):
    def __init__(self, **kwargs):
        super(Proxies, self).__init__(**kwargs)

        parser = reqparse.RequestParser()
        parser.add_argument('https', type=int, choices=[1], location='args')
        parser.add_argument('type', type=int, choices=[1,2], location='args')
        parser.add_argument('region', type=str, location='args')
        self.args = parser.parse_args()

    def get(self):
        result = {
            "data": []
        }

        options = {
            "https": bool(self.args.get('https')),
            "proxy_type": self.args.get('type'),
            "proxy_region": self.args.get('region'),
        }

        data = proxy_manager.getAllUsefulProxy(**options)
        
        for item in data:
            del item["_id"]

        result["data"] = data

        return result

class ProxyCounter(dict):
     def __missing__(self, key):
        result = 0
        if key in ["region_list", "https", "proxy_type", "last_status", "available_rate"]:
            result = ProxyCounter()
            self[key] = result

        return result


def stat(data):
    result = ProxyCounter()

    for item in data:
        for k, v in item.items():
            if k == "region_list":
                for region in v:
                    result[k][region] = result[k][region] + 1
            elif k == "https":
                result[k][v] = result[k][v] + 1
            elif k == "proxy_type":
                result[k][v] = result[k][v] + 1
            elif k == "last_status":
                result[k][v] = result[k][v] + 1
            elif k == "available_rate":
                v = int(v * 10) * 10
                result[k][v] = result[k][v] + 1

    return result

class ProxiesStat(Resource):
    def get(self):
        result = {}

        data = proxy_manager.getUsefulProxyStat()
        result["data"] = stat(data)

        return result

def init_api(app):
    @app.errorhandler(404)
    def miss(e):
        data = [
            {"result": "not found"},
            {"status_code": 404},
            {"github": "https://github.com/1again/ProxyPool"},
            {"api_list": API_LIST},
        ]
        result = jsonify(data)
        return result, 404


def init_app(app):
    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
    init_api(app)

    api = Api(app)
    api.add_resource(ProxiesStat, '/api/v1/proxies/stat/')
    api.add_resource(Proxies, '/api/v1/proxies/')
    api.add_resource(Proxy, '/api/v1/proxy/')
    api.add_resource(ApiList, '/api/v1/')
