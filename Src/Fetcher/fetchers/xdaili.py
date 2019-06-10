
# -*- coding: utf-8 -*-
# !/usr/bin/env python

import re

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree


class CustomFetcher():

    fetcher_host = "www.xdaili.cn"

    def run(self):

        url = 'http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10'
        request = WebRequest()
        try:
            res = request.get(url).json()
            for row in res['RESULT']['rows']:
                yield '{}:{}'.format(row['ip'], row['port'])
        except Exception as e:
            pass
