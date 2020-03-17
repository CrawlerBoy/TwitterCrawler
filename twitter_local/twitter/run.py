#coding:utf8

import shutil
import os
import logging
try:
    from twitter.util.driver import TwitterDriver
except:
    pass
from scrapy import cmdline
import time
import urllib2
import uuid
from codecs import open
import chardet
import pickle

import subprocess
def crawl_task():
    accounts = ['BJP4India']
     # 简介
    subprocess.call('scrapy crawl twitter_increment -a task_type=about -a driver_type=chrome -a accounts=%s --nolog' % ",".join(accounts), shell=True)
    # 关注者
    subprocess.call('scrapy crawl twitter_increment -a task_type=follower -a driver_type=followers -a accounts=%s --nolog' % ",".join(accounts), shell=True)
    # 关注的人
    subprocess.call('scrapy crawl twitter_increment -a task_type=fllowing -a driver_type=firefox -a accounts=%s --nolog' % ",".join(accounts), shell=True)
    # 推文
    subprocess.call('scrapy crawl twitter_increment -a task_type=tweet -a driver_type=firefox -a accounts=%s --nolog' % ",".join(accounts),shell=True)
    #喜欢
    subprocess.call('scrapy crawl twitter_increment -a task_type=like -a driver_type=firefox -a accounts=%s --nolog' % ",".join(accounts), shell=True)

crawl_task()

