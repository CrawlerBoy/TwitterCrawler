# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TwitterItem(scrapy.Item):
    data = scrapy.Field()
    data_type = scrapy.Field()

class PageSourceItem(scrapy.Item):
    data_type = scrapy.Field()
    html = scrapy.Field()
    twitter_id = scrapy.Field()
    tweet_id = scrapy.Field()
    file_name = scrapy.Field()

class TwitterAboutItem(scrapy.Item):
    data_type = scrapy.Field()
    account_id = scrapy.Field()
    data = scrapy.Field()

class TwitterTweetsItem(scrapy.Item):
    data_type = scrapy.Field()          #采集数据类型
    account_id = scrapy.Field()         #采集账号
    tweet_id = scrapy.Field()           #推文ID
    tweet_image_link = scrapy.Field()   #推文配图URL
    tweet_author = scrapy.Field()       #推文作者
    tweet_content = scrapy.Field()      #推文内容
    tweet_time = scrapy.Field()         #推文发布时间
    twitter_trunsmit = scrapy.Field()   #推文转载数
    twitter_like = scrapy.Field()       #推文喜欢数
    twitter_reply = scrapy.Field()      #推文回复数
    collect_time = scrapy.Field()       #采集时间
    image_path = scrapy.Field()         #图片路径
    tweet_url = scrapy.Field()          #推文URL
    video_path = scrapy.Field()         #视频路径

class TwitterLikeItem(scrapy.Item):
    data_type = scrapy.Field()
    account_id = scrapy.Field()
    data = scrapy.Field()

class TwitterFllowerItem(scrapy.Item):
    data_type = scrapy.Field()
    account_id = scrapy.Field()
    data = scrapy.Field()

class TwitterFllowingItem(scrapy.Item):
    data_type = scrapy.Field()
    account_id = scrapy.Field()
    data = scrapy.Field()

class TwitterCommentItem(scrapy.Item):
    comment_id = scrapy.Field()
    tweet_id = scrapy.Field()
    comment_name = scrapy.Field()
    comment_author_id = scrapy.Field()
    comment_content = scrapy.Field()
    comment_date = scrapy.Field()
    data_type = scrapy.Field()

