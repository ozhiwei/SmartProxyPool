# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     utilFunction.py
   Description :  tool function
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: 添加robustCrawl、verifyProxy、getHtmlTree
-------------------------------------------------
"""
import requests
import time
import re
from lxml import etree

from Util.WebRequest import WebRequest

# noinspection PyPep8Naming
def robustCrawl(func):
    def decorate(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            pass
            # logger.info(u"sorry, 抓取出错。错误原因:")
            # logger.info(e)

    return decorate


# noinspection PyPep8Naming
def verifyProxyFormat(proxy):
    """
    检查代理格式
    :param proxy:
    :return:
    """
    import re
    verify_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"
    _proxy = re.findall(verify_regex, proxy)
    return True if len(_proxy) == 1 and _proxy[0] == proxy else False


# noinspection PyPep8Naming
def getHtmlTree(url, **kwargs):
    """
    获取html树
    :param url:
    :param kwargs:
    :return:
    """

    header = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
    }
    # TODO 取代理服务器用代理服务器访问
    wr = WebRequest()

    # delay 2s for per request
    # time.sleep(2)

    html = wr.get(url=url, header=header).content
    try:
        result = etree.HTML(html)
    except Exception as e:
        # print("getHtmlTree error: ", url, e)
        result = etree.HTML("<html></html>")

    return result


def tcpConnect(proxy):
    """
    TCP 三次握手
    :param proxy:
    :return:
    """
    from socket import socket, AF_INET, SOCK_STREAM
    s = socket(AF_INET, SOCK_STREAM)
    ip, port = proxy.split(':')
    result = s.connect_ex((ip, int(port)))
    return True if result == 0 else False


# TODO: 逻辑应该有问题, 但不确定
# http是可用的才会保存https, 会不会有只开通https的代理呢?
def validUsefulProxy(proxy):
    """
    检验代理是否可用
    :param proxy:
    :return:
    """
    if isinstance(proxy, bytes):
        proxy = proxy.decode('utf8')
    proxies = {
        "http": proxy,
        "https": proxy,
    }
    http_url = "http://httpbin.org/ip"
    https_url = "https://httpbin.org/ip"

    http_result = False
    https_result = False

    # http valid
    try:
        r = requests.get(http_url, proxies=proxies, timeout=10, verify=False)

        content = r.content
        if isinstance(content, bytes):
            content = content.decode('utf8')

        status_result = r.status_code == 200
        content_result = re.search("\"origin\"", content) != None
        if status_result and content_result:
            http_result = True

    except Exception as e:
        # print(str(e))
        http_result = False

    if http_result:

        # https vaild
        try:
            r = requests.get(https_url, proxies=proxies, timeout=10, verify=False)

            content = r.content
            if isinstance(content, bytes):
                content = content.decode('utf8')

            status_right = r.status_code == 200
            content_right = re.search("\"origin\"", content) != None
            if status_right and content_right:
                https_result = True

        except Exception as e:
            # print(str(e))
            https_result = False

    return (http_result, https_result)