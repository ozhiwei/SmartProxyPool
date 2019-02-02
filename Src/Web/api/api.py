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

        options = {
            "https": bool(self.args.get('https')),
            "type": self.args.get('type'),
            "region": self.args.get('region'),
        }

        item = proxy_manager.getSampleUsefulProxy(**options)
        if item:
            del item["_id"]

        result["data"] = item

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
            "type": self.args.get('type'),
            "region": self.args.get('region'),
        }

        data = proxy_manager.getAllUsefulProxy(**options)
        
        for item in data:
            del item["_id"]

        result["data"] = data

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
    api.add_resource(Proxies, '/api/v1/proxies/')
    api.add_resource(Proxy, '/api/v1/proxy/')
    api.add_resource(ApiList, '/api/v1/')
