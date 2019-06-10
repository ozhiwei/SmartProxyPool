# -*- coding: utf-8 -*-
# !/usr/bin/env python


class Fetcher():

    fetcher_host = "cn-proxy.com"

    def __init__(self):
        split_list = self.fetcher_host.split('.')
        split_length = len(split_list)
        if split_length == 4:
            name = split_list[-3]
        else:
            name = split_list[-2]

        self.fetcher_name = name

