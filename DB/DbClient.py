# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：    DbClient.py
   Description :  DB工厂类
   Author :       JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys

from Util.GetConfig import config
from Util.utilClass import Singleton

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DbClient(object):
    """
    DbClient DB工厂类 提供get/put/pop/delete/getAll/changeTable方法

    目前存放代理的table/collection/hash有两种：
        raw_proxy： 存放原始的代理；
        useful_proxy_queue： 存放检验后的代理；

    抽象方法定义：
        get(proxy): 返回proxy的信息；
        put(proxy): 存入一个代理；
        pop(): 弹出一个代理
        exists(proxy)： 判断代理是否存在
        getNumber(raw_proxy): 返回代理总数（一个计数器）；
        update(proxy, num): 修改代理属性计数器的值;
        delete(proxy): 删除指定代理；
        getAll(): 返回所有代理；
        changeTable(name): 切换 table or collection or hash;


        所有方法需要相应类去具体实现：
            SSDB：SsdbClient.py
            REDIS:RedisClient.py

    """

    __metaclass__ = Singleton

    def __init__(self):
        """
        init
        :return:
        """
        self.__initDbClient()

    def __initDbClient(self):
        """
        init DB Client
        :return:
        """
        __type = None
        if "SSDB" == config.db_type:
            __type = "SsdbClient"
        elif "REDIS" == config.db_type:
            __type = "RedisClient"
        elif "MONGODB" == config.db_type:
            __type = "MongodbClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(config.db_type)
        self.client = getattr(__import__(__type), __type)(name=config.db_name,
                                                          host=config.db_host,
                                                          port=config.db_port,
                                                          username=config.db_username,
                                                          password=config.db_password)
    # unuseful function
    # def get(self, key, **kwargs):
    #     query = {"proxy": key}
    #     data = self.client.get(query)
    #     return data

    # unuseful function
    # def put(self, key, **kwargs):
    #     return self.client.put(key, **kwargs)

    # unuseful function
    # def update(self, query, data):
    #     return self.client.update(query, data)

    # unuseful function
    # def delete(self, key):
    #     return self.client.delete(key, **kwargs)

    # unuseful function
    # def exists(self, key, **kwargs):
    #     return self.client.exists(key, **kwargs)

    # unuseful function
    # def pop(self, **kwargs):
    #     return self.client.pop(**kwargs)

    def getAll(self):
        return self.client.getAll()

    def changeTable(self, name):
        self.client.changeTable(name)

    # unuseful function
    # def getNumber(self):
    #     return self.client.getNumber()

    def getAllUsefulProxy(self):
        table_name = "useful_proxy"
        self.changeTable(table_name)

        result = self.client.getAll()
        return result

    def getAllRawProxy(self):
        table_name = "raw_proxy"
        self.changeTable(table_name)

        result = self.client.getAll()
        return result

    def checkRawProxyExists(self, proxy):
        query = {"proxy": proxy}
        self.client.exists(query)

    # TODO: refine function
    def getSampleUsefulProxy(self, usable_rate):
        result = None
        table_name = "useful_proxy"
        self.client.changeTable(table_name)
        operation_list = 	[
            {
                "$match": {"total": { "$ne": 0}}
            },
            {
                "$project": { "proxy": 1, "usable_rate": { "$divide": ["$succ", "$total"] } }
            },
            {
                "$project": { "proxy": 1, "usable_rate": { "$multiply": ["$usable_rate", 100] } }
            },
            { 
                "$match": { "usable_rate": { "$gte": usable_rate}}
            },	
            {
                "$sample": { "size": 1}
            },
        ]
        data = self.client.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    # TODO: refine function
    def getSampleRawProxy(self):
        result = None
        table_name = "raw_proxy"
        self.client.changeTable(table_name)
        operation_list = 	[
            {
                "$sample": { "size": 1}
            },
        ]
        data = self.client.aggregate(operation_list)
        if data:
            result = data[0]

        return result

    def getProxyNum(self, table_name):
        self.client.changeTable(table_name)
        num = self.client.find().count()

        return num

    def saveRawProxy(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        data = {"proxy": proxy, "succ": 0, "fail": 0, "total": 0}
        self.client.put(query, data)

    def saveUsefulProxy(self, proxy, data):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.put(query, data)

    def deleteUsefulProxy(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.delete(query)

    def deleteRawProxy(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)
        query = {"proxy": proxy}
        self.client.delete(query)

    def tickUsefulProxyVaildSucc(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'succ': 1}}
        self.client.update(query, data)

    def tickUsefulProxyVaildFail(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'fail': 1}}
        self.client.update(query, data)

    def tickUsefulProxyVaildTotal(self, proxy):
        table_name = 'useful_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.client.update(query, data)

    def tickRawProxyVaildSucc(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'succ': 1}}
        self.client.update(query, data)

    def tickRawProxyVaildFail(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'fail': 1}}
        self.client.update(query, data)

    def tickRawProxyVaildTotal(self, proxy):
        table_name = 'raw_proxy'
        self.client.changeTable(table_name)

        query = {"proxy": proxy}
        data = {'$inc': {'total': 1}}
        self.client.update(query, data)

if __name__ == "__main__":
    # account = DbClient()
    # print(account.get())
    # account.changeTable('use')
    # account.put('ac')
    # print(account.get())
    pass
