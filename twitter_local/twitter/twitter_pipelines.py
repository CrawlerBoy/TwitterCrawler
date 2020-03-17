# -*- coding: utf-8 -*-

import datetime
import os
import json
from codecs import open 
import redis
from twitter.items import PageSourceItem,TwitterAboutItem,TwitterTweetsItem,TwitterLikeItem,TwitterFllowerItem,TwitterFllowingItem

class TwitterPipeline(object):

    def __init__(self):
        self.db = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.DATA_FILE_PATH = {
            "about": "twitter_data/texts",
            "tweet": "twitter_data/texts",
            "follower": "twitter_data/texts",
            "following": "twitter_data/texts",
            "like": "twitter_data/texts",
            "comment": "twitter_data/texts"
        }
        self.PAGE_FILE_PATH = {
            "about":"data_source/twitter_data/sometime_dir/html/somebody_twitter_id/about",
            "tweet" :"data_source/twitter_data/sometime_dir/html/somebody_twitter_id/tweets",
            "fllower":"data_source/twitter_data/sometime_dir/html/somebody_twitter_id/fllowers",
            "following":"data_source/twitter_data/sometime_dir/html/somebody_twitter_id/fllowing",
            "like": "data_source/twitter_data/sometime_dir/html/somebody_twitter_id/like",
        }

    def process_item(self, item, spider):
        print("===> in pipeline")
        date_time = datetime.datetime.now().strftime("%Y%m%d")
        data_type = item.get("data_type")
        if data_type == "comment":
            if not item.get("comment_date"):
                print "Not CommentInfo========================>>"
            else:
                data_path = self.DATA_FILE_PATH.get(data_type)
                if not os.path.exists(data_path):
                    os.makedirs(data_path)
                data = json.dumps(dict(item),ensure_ascii=False)
                full_file_path = os.path.join(data_path, "%sdata"%data_type)
                with open(full_file_path,"a",encoding="utf-8") as twitter:
                    twitter.write(data+"\n")
        elif data_type == "following":
            if item.get("file_name"):
                pass
            else:
                data_path = self.DATA_FILE_PATH.get(data_type)
                if not os.path.exists(data_path):
                    os.makedirs(data_path)
                data = json.dumps(dict(item),ensure_ascii=False)
                full_file_path = os.path.join(data_path, "%sdata"%data_type)
                with open(full_file_path,"a",encoding="utf-8") as twitter:
                    twitter.write(data+"\n")
        # if isinstance(item, PageSourceItem):
        #     data_path = self.PAGE_FILE_PATH.get(data_type)
        #     data_path = data_path.replace("sometime_dir", date_time)
        #     if item.get("twitter_id"):
        #         data_path=data_path.replace("somebody_twitter_id", item.get("twitter_id"))
        #     if item.get("tweet_id"):
        #         data_path=data_path.replace("some_tweet_id", item.get("tweet_id"))
        #     if not os.path.exists(data_path):
        #         os.makedirs(data_path)
        #     file_name = item.get("file_name")
        #     full_file_path = os.path.join(data_path, file_name)
        #     data=item.get("html")
        #     with open(full_file_path,"w",encoding="utf-8") as twitter:
        #         twitter.write(data)
        #     print "==> write file done: %s" % full_file_path
        #     self.db.set(item.get("twitter_id")+"#"+data_type, 1)
        #     print "==> scave data to redis"
        else:
            data_path = self.DATA_FILE_PATH.get(data_type)
            #data_path = data_path.replace("sometime_dir", date_time)
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            data = json.dumps(dict(item),ensure_ascii=False)
            full_file_path = os.path.join(data_path, "%sdata"%data_type)
            with open(full_file_path,"a",encoding="utf-8") as twitter:
                twitter.write(data+"\n")
        print("===> finished pipeline ==>")
        return item

        
