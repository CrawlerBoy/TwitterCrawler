#!/usr/bin/env python
# coding:utf8

from scrapy import  Selector
from codecs import open
from collections import OrderedDict
import random, subprocess
import time
import logging
import json, youtube_dl
import sys
import re, hashlib, redis
import datetime, dateparser
from twitter.settings import DATA_REPORT_API, LOG_REPORT_API, STATUS_REPORT_API
from twitter.items import PageSourceItem,TwitterAboutItem,TwitterTweetsItem,TwitterLikeItem,TwitterFllowerItem,TwitterFllowingItem,TwitterCommentItem
from copy import deepcopy
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

global tweet_list
tweet_list = set()


class TweetParseTools(object):
    green = "\033[1;32;40m  %s  \033[0m"
    red = "\033[31;1m  %s  \033[0m"
    
    def __init__(self):
        self.pc_ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        self.mb_ua = "Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0"
        self.green = "\033[1;32;40m  %s  \033[0m"

    # 随机等待
    def sleep_random_float(self):
        num = round(float(random.randint(10, 15)) / random.randint(8, 10), 2)
        logging.info("==>sleep {} seconds".format(num))
        time.sleep(num)

    # 时间转换器
    def _time_converter(self, date):
        if u'年' not in date and u'月' in date:
            date = str(datetime.date.today())[:4] + u'年' + date 
        t = dateparser.parse(date)
        if t is None:
            return date
        else:
            l = t.strftime('%Y-%m-%d %H:%M:%S')
        return l


class TweetPcParser(TweetParseTools):

    def __init__(self, driver, task_json):
        self.domain = "https://twitter.com/"
        self.tweet_user_id = task_json.get("account")
        self.driver=driver
        

    #获取PC端简介
    def parse_about(self):
        about_page_item = PageSourceItem()
        try:
            self.driver.get(self.domain + self.tweet_user_id)
            self.sleep_random_float()
            #解析简介Item
            about_item = TwitterAboutItem()
            self.selector = Selector(text=self.driver.page_source)
            item = OrderedDict()
            tweet_user_id = self.selector.xpath("//div[@class='ProfileHeaderCard']/h2/a/span/b/text()").extract_first(default="")
            name = self.selector.xpath("//div[@class='ProfileHeaderCard']/h1[@class='ProfileHeaderCard-name']/a/text()").extract_first(default="")
            bio = self.selector.xpath("//div[@class='ProfileHeaderCard']/p[contains(@class,'ProfileHeaderCard-bio')]").xpath("string(.)").extract_first(default="")
            avatar = self.selector.xpath("//div[@class='ProfileAvatar']/a/img/@src").extract_first(default="")
            location = self.selector.xpath("//div[@class='ProfileHeaderCard']/div[contains(@class,'ProfileHeaderCard-location')]/span/text()").extract_first(default="")
            join_date = self.selector.xpath("//div[@class='ProfileHeaderCard']/div[@class='ProfileHeaderCard-joinDate']/span[contains(@class,'ProfileHeaderCard-joinDateText')]/@title").extract_first(default="")
            join_date = self._time_converter(join_date)
            atter_keys={"tweets":"--tweets", "following":"--following", "followers":"--followers", "favorites":"--favorites", }
            item["tweet_user_id"]=tweet_user_id
            item["name"]=name
            item["bio"]=bio
            item["avatar"]=avatar
            item["location"]=location
            item["join_date"]=join_date
            for key,value in atter_keys.items():
                value = self.selector.xpath("//div[@class='ProfileNav']/ul/li[contains(@class,'%s')]/a/span[@class='ProfileNav-value']/text()" % value).extract_first(default="")
                item[key] = value
            for key,value in item.items():
                item[key] = value.strip()
            item["inserttime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item["account_id"]=self.tweet_user_id
            item["data_type"] = 'about'
            yield item
            self.driver.quit()
        except Exception as e:
            about_page_item["error"]=e.message


class TweetMbParser(TweetParseTools):

    def __init__(self, driver, task_data):
        self.rdb = redis.Redis(host='127.0.0.1',port=6379,db=0)
        self.domain = "https://mobile.twitter.com"
        self.driver = driver
        self.tweet_user_id = task_data['account']
        self.task_data = task_data
        super(TweetMbParser, self).__init__()        

    #解析推文列表
    def parse_tweet_list(self, page_type="tweet", flag=40):
        logging.info("==>get {}".format(page_type))
        try:
            if page_type == "tweet":
                tweet_link = "https://mobile.twitter.com/" + self.tweet_user_id 
                # tweet_link = "https://mobile.twitter.com/SuPriyoBabul?max_id=1112371935696949249" 
                self.driver.get(tweet_link)
                self.sleep_random_float()
            while True:
                logging.info("==>{} list".format(page_type))
                follower_html = self.driver.page_source
                selector = Selector(text=follower_html)
                elements = selector.xpath("//div[@class='{}']/table[contains(@class,'tweet')]".format("timeline" if page_type=="tweet" else "timeline replies")) 
                for ele in elements:
                    tweet_link = ele.xpath("@href").extract_first(default="")
                    if self.tweet_user_id in tweet_link:
                        tweet_list.add("https://www.twitter.com" + tweet_link)
                if len(tweet_list) >= flag:  
                    for tweet_detail_comment_item in self.parse_tweet_detail_seq(tweet_list):
                        yield tweet_detail_comment_item
                more_button_list = self.driver.find_elements_by_xpath("//div[@class='w-button-more']/a")
                if more_button_list:
                    self.driver.execute_script("window.scrollBy(0,10000)")
                    time.sleep(1)
                    more_button_list[0].click() 
                    self.sleep_random_float()
                else:
                    logging.info(u"\n==>no more tweets found")
                    if tweet_list:
                        for tweet_detail_comment_item in self.parse_tweet_detail_seq(tweet_list):
                            yield tweet_detail_comment_item
                    break
        except Exception as e:
            logging.error(u"==>tweet_list error：%s" % e)

    def set_bool_preferce(self, name, value):
        value = 'true' if value else 'false';
        self.driver.execute_script("""
            document.getElementById("textbox").value = arguments[0];
            FilterPrefs();
            view.selection.currentIndex = 0;
            if (view.rowCount == 1) {
               current_value = view.getCellText(0, {id:"valueCol"});
               if (current_value != arguments[1]) {
                   ModifySelected();
               }
            } 
        """, name, value)

    def set_string_preferce(self, name, value):
        modified = self.driver.execute_script("""
            document.getElementById("textbox").value = arguments[0];
            FilterPrefs();
            view.selection.currentIndex = 0;
            if (view.rowCount == 1) {
               current_value = view.getCellText(0, {id:"valueCol"});
               if (current_value != arguments[1]) {
                   ModifySelected();
                   return true;
               }
            } 
            return false;
        """, name, value)
        if modified is None or modified is True:
            time.sleep(3)
            alert = self.driver.switch_to.alert
            alert.send_keys(value)
            time.sleep(2)
            alert.accept()

    def parse_tweet_detail_seq(self, tweet_list):
        detail_data = []
        handles = self.driver.window_handles
        self.driver.switch_to_window(handles[1])
        logging.info("==>get tweet detail")
        self.driver.get("about:config")
        self.set_string_preferce("general.useragent.override", self.pc_ua)       
        for tweet_detail_link in deepcopy(tweet_list):
            for item in self.parse_tweet_detail(tweet_detail_link):
                print self.green % json.dumps(dict(item), ensure_ascii=False, indent=4)
                yield item
                #detail_data.append(item)
            tweet_list.remove(tweet_detail_link)
        self.driver.get("about:config")
        self.set_string_preferce("general.useragent.override", self.mb_ua)
        self.driver.switch_to_window(handles[0])
        #return detail_data

    def rename_hook(self, d): 
        if d['status'] == 'finished':
            print(self.green % 'Done Downloading!!!')

    #视频下载函数           
    def download(self,download_url, md5_url):
            ydl_opts = { 
                #'format': 'bestvideo[ext=mp4]',
                'outtmpl':'../twitter_data/videos/%s.mp4'%(md5_url),
                'progress_hooks': [self.rename_hook],
                'writeautomaticsub':True,
                'subtitleslangs':'en',
                'proxy':'127.0.0.1:8118'
            }  
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([download_url])

    #解析推文内容
    def parse_tweet_detail(self, tweet_detail_link, page_html=False):
        item = TwitterCommentItem()
        tweet_item = TwitterTweetsItem()
        tweet_id_pa = re.compile(ur"status/(.*)\?")
        #self.driver.execute_script("window.open()")
        if self.rdb.get(tweet_detail_link):
            print self.red % "Already Collect"
        else:
            self.driver.get(tweet_detail_link)
            time.sleep(6)
            self.rdb.set(tweet_detail_link,1)
            comment_num = 0
            while True:
                more_before = self.driver.page_source
                print "more_before",len(more_before) 
                down = self.driver.find_element_by_class_name("trends-inner")
                self.driver.execute_script("arguments[0].scrollIntoView();", down)
                comment_num += 1
                time.sleep(2)
                more_after = self.driver.page_source
                print "more_after：",len(more_after)
                if len(more_after) - len(more_before) < 500 or comment_num > 2:
                    break
                print u"拖动成功－－－－－－"
            source = self.driver.page_source
            selector_object = Selector(text=source)
            tweet_user_id_pa = re.compile(ur"twitter.com/(.*)/status")
            tweet_item['account_id'] = self.tweet_user_id
            tweet_item['tweet_id'] = tweet_id_pa.findall(tweet_detail_link)[0]
            tweet_item['tweet_author'] = selector_object.xpath("//span[@class='FullNameGroup']/strong/text()").extract_first(default="")
            tweet_content_ele = selector_object.xpath("//p[@class='TweetTextSize TweetTextSize--jumbo js-tweet-text tweet-text']").xpath("string(.)").extract_first(default="")
            tweet_item['tweet_content'] = tweet_content_ele.replace("\n","")
            tweet_time_ele = selector_object.xpath("//span[@class='metadata']").xpath('string(.)').extract_first(default="")
            tweet_item['tweet_time'] = self._time_converter(tweet_time_ele.strip().replace("\n","")) if tweet_time_ele else None
            tweet_time = self._time_converter(tweet_time_ele.strip()) if tweet_time_ele else None
            if tweet_time < "2019-01-01":
               self.driver.quit()
            tweet_item['twitter_trunsmit'] = selector_object.xpath("//li[@class='js-stat-count js-stat-retweets stat-count']/a/strong/text()").extract_first(default="")
            tweet_item['twitter_like'] = selector_object.xpath("//li[@class='js-stat-count js-stat-favorites stat-count']/a/strong/text()").extract_first(default="")
            tweet_item["tweet_url"] = tweet_detail_link
            
            twitter_img = selector_object.xpath("//div[@class='permalink-inner permalink-tweet-container']/div//div/img/@src").extract()
            image_md5_url = None
            if len(twitter_img) == 1:
                url_md5 = hashlib.md5(u"%s".encode('utf8')% twitter_img[0]).hexdigest()
                subprocess.call('''youtube-dl --proxy 127.0.0.1:8118 -o "../twitter_data/images/%s.jpg" %s \
                    --external-downloader aria2c --external-downloader-args "-x 16 -k 1M"'''%(url_md5, twitter_img[0]), shell=True)
                image_md5_url = "images" + "/" + hashlib.md5(u"%s".encode('utf8')% twitter_img[0]).hexdigest() + ".jpg"
                tweet_item['tweet_image_link'] = twitter_img[0]
            elif len(twitter_img) > 1:
                img_list = []
                image_md5_url = []
                for img in twitter_img:
                    url_md5 = hashlib.md5(u"%s".encode('utf8')% img).hexdigest()
                    subprocess.call('''youtube-dl --proxy 127.0.0.1:8118 -o "../twitter_data/images/%s.jpg" %s'''%(url_md5, img), shell=True)
                    img_md5_url = "images" + "/" + hashlib.md5(u"%s".encode('utf8')% img).hexdigest() + ".jpg"
                    image_md5_url.append(img_md5_url)
                    img_list.append(img)
                    tweet_item['tweet_image_link'] = img_list
            if image_md5_url:
                tweet_item['image_path'] = image_md5_url
            else:
                tweet_item['image_path'] = ""
            twitter_num = selector_object.xpath("//span[@class='ProfileTweet-actionCountForAria']/text()").extract()
            if len(twitter_num) > 0:
                tweet_item['twitter_reply'] = twitter_num[0].replace(u'回复','')
            tweet_item["collect_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            tweet_item['data_type'] = "tweet"
            yield tweet_item

            twitter_comment_ele = selector_object.xpath('//li[@class="js-stream-item stream-item stream-item\n"]').extract()
            for comment_info in twitter_comment_ele:
                select_comment = Selector(text=comment_info)
                comment_date= select_comment.xpath('//small[@class="time"]/a/@title').extract_first(default="")
                if comment_date:
                    item['comment_id'] = select_comment.xpath("//li[@class='js-stream-item stream-item stream-item\n']/@data-item-id").extract_first(default="")
                    item['tweet_id'] = tweet_id_pa.findall(tweet_detail_link)[0]
                    item['comment_name'] = select_comment.xpath('//div[@class="stream-item-header"]/a/span[@class="FullNameGroup"]/strong/text()').extract_first(default="")
                    item['comment_author_id'] = select_comment.xpath('//span[@class="username u-dir u-textTruncate"]/b/text()').extract_first(default="")
                    item['comment_content'] = select_comment.xpath('//p[@class="TweetTextSize  js-tweet-text tweet-text"]').xpath('string(.)').extract_first(default="")
                    comment_date_ele = select_comment.xpath('//small[@class="time"]/a/@title').extract_first(default="")
                    item['comment_date'] = self._time_converter(comment_date_ele) 
                    item['data_type'] = 'comment'
                    item["account_id"] = self.tweet_user_id
                    yield item
                else:
                    pass

    def parse_commnet(self):
        return self.parse_tweet_list(page_type="comment")

    def parse_like(self):
        like_link = "https://mobile.twitter.com/" + self.tweet_user_id + "/favorites"
        self.driver.get(like_link)
        self.sleep_random_float()
        cursor = 0
        like_list = []
        while True:
            logging.info("==> like list")
            like_html = self.driver.page_source

            selector = Selector(text=like_html)
            elements = selector.xpath("//div[@class='{}']/table[contains(@class,'tweet')]".format("timeline"))
            for ele in elements:
                tweet_link = ele.xpath("@href").extract_first(default="")
                item = OrderedDict()
                item["like_tweet_author_avatar"] = ele.xpath("tbody/tr/td[contains(@class,'avatar')]/a/img/@src").extract_first(default="")
                like_tweet_author_link = ele.xpath("tbody/tr/td[contains(@class,'user-info')]/a/@href").extract_first(default="")
                item["like_tweet_author_link"] = "https://mobile.twitter.com/" + like_tweet_author_link
                like_tweet_author_tweeter_id = ele.xpath("tbody/tr/td[contains(@class,'user-info')]/a/div[@class='username']/text()").extract()
                item["like_tweet_author_tweeter_id"] = "".join(like_tweet_author_tweeter_id).replace("\n","").replace(" ","")
                item["like_tweet_author_name"] = ele.xpath("tbody/tr/td[contains(@class,'user-info')]/a/strong/text()").extract_first(default="").strip()
                item["like_tweet_id"] = ele.xpath("tbody/tr[@class='tweet-container']/td[@class='tweet-content']/div[@class='tweet-text']/@data-id").extract_first(default="").strip()
                item["like_tweet_content"] = ele.xpath("tbody/tr[@class='tweet-container']/td[@class='tweet-content']/div[@class='tweet-text']").xpath("string(.)").extract_first(default="").strip()
                item["account_id"] = self.tweet_user_id
                item["tweet_link"] = tweet_link

                item["data_type"] = 'like'
                yield item
            more_like = self.driver.find_elements_by_xpath("//div[@class='w-button-more']/a")
            if more_like:
                more_like[0].click()
                self.sleep_random_float()
                continue
            else:
                break

    #解析正在关注
    def parse_fllowing(self):

        logging.info("==>get following")
        following_list = []
        try:
            follower_link = "https://mobile.twitter.com/" + self.tweet_user_id + "/following"
            self.driver.get(follower_link)
            self.sleep_random_float()
            cursor = 0
            count_data = 0
            while True:
                logging.info("==> follwer list")
                if count_data > 50:
                    self.driver.quit()
                following_html = self.driver.page_source
                fllowing_page_item = PageSourceItem()
                fllowing_page_item["data_type"] = "following"
                fllowing_page_item["twitter_id"] = self.tweet_user_id
                fllowing_page_item["html"] = following_html
                fllowing_page_item["file_name"] = "following%s.html" % cursor
                yield fllowing_page_item
                selector = Selector(text=self.driver.page_source)
                elements = selector.xpath("//div[@class='user-list']/table")
                for user in elements:
                    fllowing_item = TwitterFllowingItem()
                    image_link = user.xpath('tbody/tr/td/img[contains(@src,"twimg.com")]/@src').extract_first()
                    follower_name = user.xpath('tbody/tr/td/a/strong/text()').extract_first()
                    follower_id = user.xpath("tbody/tr/td/a/span/text()").extract_first()
                    item = OrderedDict()
                    item["following_from"] = self.tweet_user_id
                    item["following_to"] = follower_id
                    item["following_name"] = follower_name
                    item["following_image_link"] = image_link

                    item['data_type']='following'
                    yield item
                more_follower = self.driver.find_elements_by_xpath("//div[@class='w-button-more']/a")
                if more_follower:
                    more_follower[0].click()
                    count_data += 1
                    self.sleep_random_float()
                    continue
                else:
                    break
        except Exception as e:
            logging.info("==>followering link error：%s" % e) 
        logging.info("==>following[%s]" % len(following_list))

    #解析关注者
    def parse_followers(self):
        logging.info("==>get followers")
        follower_list = []
        try:
            follower_link = "https://mobile.twitter.com/" + self.tweet_user_id + "/followers"
            self.driver.get(follower_link)
            self.sleep_random_float()
            cursor=0
            data_count = 0
            while True:
                logging.info("==> follwer list")
                if data_count > 50:
                    self.driver.quit()
                follower_html = self.driver.page_source
                fllower_page_item = PageSourceItem()
                fllower_page_item["data_type"] = "fllower"
                fllower_page_item["twitter_id"] = self.tweet_user_id

                selector = Selector(text=self.driver.page_source)
                elements = selector.xpath("//div[@class='user-list']/table")
                for user in elements:
                    twitter_fllower_item = TwitterFllowerItem()
                    image_link = user.xpath('tbody/tr/td/img[contains(@src,"twimg.com")]/@src').extract_first()
                    follower_name = user.xpath('tbody/tr/td/a/strong/text()').extract_first()
                    follower_id = user.xpath("tbody/tr/td/a/span/text()").extract_first()
                    item = OrderedDict()
                    item["follower_from"] = self.tweet_user_id
                    item["follower_to"] = follower_id
                    item["follower_name"] = follower_name
                    item["follower_image_link"] = image_link

                    item['data_type'] = 'follower'
                    yield item
                more_follower = self.driver.find_elements_by_xpath("//div[@class='w-button-more']/a")
                if more_follower:
                    more_follower[0].click()
                    data_count += 1
                    self.sleep_random_float()
                    continue
                else:
                    break
            self.driver.quit()
        except Exception as e:
            logging.info(u"==>Followers link error：%s" % e) 
        logging.info("==>followers[%s]" % len(follower_list)) 

