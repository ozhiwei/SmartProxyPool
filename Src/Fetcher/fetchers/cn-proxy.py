
# -*- coding: utf-8 -*-
# !/usr/bin/env python

import re

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree


class CustomFetcher():

    fetcher_host = "cn-proxy.com"

    def run(self):

        urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
        request = WebRequest()
        for url in urls:
            r = request.get(url)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)
