# -*- coding: utf-8 -*-
import time
import redis
import scrapy
import logging
from twitter.util.driver import TwitterDriver
from twitter.util.task_distribution import Distribution


class TwitterIncrementSpider(scrapy.Spider):

    name = 'twitter_increment'
    start_urls = ["https://twitter.com/"]

    def __init__(self, task_type, driver_type, accounts, *args, **kwards):
        self.accounts= accounts.split(",")
        print "==> accounts:",self.accounts
        self.task_type = task_type
        self.driver_type = driver_type
        self.db = redis.StrictRedis(host="localhost", port=6379, db=0)
        super(TwitterIncrementSpider, self).__init__(*args, **kwards)

    def parse(self, response):
        driver = TwitterDriver() if self.driver_type=="chrome" else TwitterDriver(mb_agent=True)
        for account in self.accounts:
            if self.db.get(account+"#"+self.task_type):
                print "==>has been scrapyd"
                continue
            time.sleep(5)
            task_data = {'type':self.task_type,'account':account}
            distribution = Distribution(task_data, driver.driver)
            report_jobs = distribution.crawl_task()
            for item in report_jobs:
                yield item

    def parse_report(self, response):
        logging.info(u"上报数据结果返回状态: %s" % response.text)

    def parse_error(self, response):
        print(dir(response))
        print(logging.error(u"上报数据结果返回状态:  {}".format(response.getErrorMessage())))


