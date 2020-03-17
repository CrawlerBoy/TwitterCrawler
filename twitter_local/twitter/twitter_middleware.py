#!/usr/bin/env python
# coding:utf-8
import scrapy
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings

class TwitterProxyMiddleware(object):

    red = "\033[31;1m  %s  \033[0m"
    blue = "\033[34;1m  %s  \033[0m"
    green = "\033[1;32;40m  %s  \033[0m"
    yellow = "\033[33;1m  %s  \033[0m"

    def process_request(self, request, spider):
        print "==> in twitter middleware"
        settings = get_project_settings()
        proxy_addr = settings['PROXY_ADDR']
        request.meta["proxy"] = proxy_addr

