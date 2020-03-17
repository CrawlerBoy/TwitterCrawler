# -*- coding: utf-8 -*-

import logging
import json
import importlib
from twitter_parser import TweetPcParser, TweetMbParser

TASK_TAGS = {
    "tweet": "TweetMbParser.parse_tweet_list",
    "like": "TweetMbParser.parse_like",
    "3": "",
    "follower": "TweetMbParser.parse_followers",
    "6": "",
    "about": "TweetPcParser.parse_about",
    "fllowing": "TweetMbParser.parse_fllowing",
}

class Distribution(object):

    def __init__(self, task_json, driver=None):
        self.task_data = task_json
        self.driver = driver
        logging.info(u"==>获取的任务JOSN: %s" % task_json)


    def crawl_task(self):
        task_tag = TASK_TAGS.get(self.task_data.get("type"))
        module_name = "twitter.util.twitter_parser"
        class_name, func_name = task_tag.split(".")
        somemodule = importlib.import_module(module_name)
        cls_obj = getattr(somemodule, class_name)(self.driver, self.task_data)
        return getattr(cls_obj,func_name)()


if __name__=="__main__":
    class_name, func_name = TASK_TAGS['7'].split(".")
    module_name = "twitter.util.twitter_parser"
    somemodule = importlib.import_module(module_name)
    print getattr(somemodule, class_name)