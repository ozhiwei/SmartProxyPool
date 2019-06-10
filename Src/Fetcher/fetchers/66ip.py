
# -*- coding: utf-8 -*-
# !/usr/bin/env python

import re

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree
from Fetcher import Fetcher


class CustomFetcher(Fetcher):

    fetcher_host = "www.66ip.cn"

    def run(self):
        area = 33
        page = 1
        for area_index in range(1, area + 1):
            for i in range(1, page + 1):
                url = "http://www.66ip.cn/areaindex_{}/{}.html".format(area_index, i)
                html_tree = getHtmlTree(url)
                tr_list = html_tree.xpath("//*[@id='footer']/div/table/tr[position()>1]")
                if len(tr_list) == 0:
                    continue
                for tr in tr_list:
                    yield tr.xpath("./td[1]/text()")[0] + ":" + tr.xpath("./td[2]/text()")[0]
                break
