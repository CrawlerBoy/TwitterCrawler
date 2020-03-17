#!coding:utf-8

import os
import re
import time
import random
import requests
import platform
import zipfile
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options


class TwitterDriver(object):
    username = "qiulin_wu590"
    password = "womendeai99.@"
    login_url = "https://mobile.twitter.com/login"

    def __init__(self, mb_agent=False):
        self.driver_path = self.process_driver()
         options = Options()
        options.add_argument("--headless")
        twitter = FirefoxProfile()
        twitter.set_preference("general.useragent.override", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/")
        #twitter.set_preference("dom.webnotifications.enabled", False)
        twitter.set_preference("general.warnOnAboutConfig", False)
        twitter.set_preference('network.proxy.type', 1)
        twitter.set_preference('network.proxy.http', '127.0.0.1')
        twitter.set_preference('network.proxy.http_port', 8118)
        twitter.set_preference("network.proxy.ssl", '127.0.0.1')
        twitter.set_preference("network.proxy.ssl_port", 8118)
        # twitter.set_preference('permissions.default.image',2)
        #twitter.set_preference('permissions.default.stylesheet',2)
        twitter.update_preferences()
        # twitter.set_preference('intl.accept_languages',"en-AU")
        # driver = webdriver.Firefox(executable_path=path, firefox_profile=twitter)
        if mb_agent:
            twitter.set_preference("general.useragent.override","Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0") 
        self.driver = webdriver.Firefox(executable_path=self.driver_path, firefox_profile=twitter, firefox_options=options)
        self.login(self.username,self.password)

    def process_driver(self):
        return 'geckodriver'
       

    def install_cookie(self):
        pass

    def sleep_random_float(self):
        num = round(float(random.randint(10, 15)) / random.randint(8, 10), 2)
        time.sleep(num)

    def login(self,username,password):
        print(u"使用用户名: %s" % username)
        print(u"使用密码: %s" % password)
        self.driver.get(self.login_url)
        #self.driver.implicitly_wait(30)
        time.sleep(10)
        user_name = self.driver.find_element_by_xpath("//input[contains(@name,'username_or_email')]")
        pass_word  = self.driver.find_element_by_xpath("//input[contains(@name,'session[password]')]")
        user_name.send_keys(username)
        pass_word.send_keys(password)
        pass_word.submit()
        print(u"==>点击登录")
        time.sleep(3)
        if self.driver.find_elements_by_id("login-challenge-form"):
            challenge_response = self.driver.find_element_by_id("challenge_response")
            challenge_response.send_keys(username.replace("+86",""))
            challenge_response.submit()
        if self.driver.current_url == "https://mobile.twitter.com/home":
            print(u"==>登录成功")

        self.driver.execute_script("window.open()")

    def search_account(self,tag):
        search_url = u"https://mobile.twitter.com/search?q=%s&s=typd&x=19&y=11" % tag
        self.driver.get(search_url)
        more_user_link = self.driver.find_elements_by_xpath("//div[@class='user-list-more']/a")
        if more_user_link:
            more_user_link[0].click()
        time.sleep(5)

    def get_twitter_username_list(self):
        user_list = self.driver.find_elements_by_xpath("//td[@class='info']/a/span[@class='username']")
        account_list = [user.text.strip("@") for user in user_list]
        return account_list


    def __del__(self):
        print("==> 关闭dirver")
        self.driver.quit()


if __name__=="__main__":

    driver = TwitterDriver()
    url = 'https://twitter.com/PresidentMa19/status/535342303330582528' 
    js = "window.scrollTo(0, Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, document.documentElement.clientHeight));"
    driver.driver.get(url)
    down = driver.driver.find_element_by_class_name("trends-inner")
    driver.driver.execute_script("arguments[0].scrollIntoView();", down)
    print "333333"
    time.sleep(20)
