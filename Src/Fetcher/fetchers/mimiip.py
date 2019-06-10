
# -*- coding: utf-8 -*-
# !/usr/bin/env python

import re

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree


class CustomFetcher():

    fetcher_host = "www.mimiip.com"

    def run(self):

        url_gngao = ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 10)]  # 国内高匿
        url_gnpu = ['http://www.mimiip.com/gnpu/%s' % n for n in range(1, 10)]  # 国内普匿
        url_gntou = ['http://www.mimiip.com/gntou/%s' % n for n in range(1, 10)]  # 国内透明
        url_list = url_gngao + url_gnpu + url_gntou

        request = WebRequest()
        for url in url_list:
            r = request.get(url)
            if r.status_code != 200:
                break
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W].*<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)
