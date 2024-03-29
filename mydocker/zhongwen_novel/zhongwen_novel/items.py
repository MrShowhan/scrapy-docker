# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhongwenNovelItem(scrapy.Item):
    # define the fields for your item here like:
    seq = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    author = scrapy.Field()
    details = scrapy.Field()
    chapter = scrapy.Field()
    url = scrapy.Field()
    _id = scrapy.Field()