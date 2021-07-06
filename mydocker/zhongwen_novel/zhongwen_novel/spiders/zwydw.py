# -*- coding: utf-8 -*-
import scrapy
from redis import StrictRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from zhongwen_novel.items import ZhongwenNovelItem

from copy import deepcopy
class ZwydwSpider(CrawlSpider):
    name = 'zwydw'
    allowed_domains = ['zwydw.com']
    start_urls = ['https://www.zwydw.com/top.html']

    rules = (
        Rule(LinkExtractor(restrict_css='.rank > div ul'), callback='parse_fiction'),
    )


    def parse_fiction(self, response):
        item = ZhongwenNovelItem()
        item['title'] = response.xpath('//div[@id="info"]/h1/text()').extract_first()   #获取小说名
        author = response.xpath('//div[@id="info"]/p/text()').extract_first()
        item['author'] = author.replace('\xa0\xa0\xa0\xa0','')                          #作者名
        details = response.xpath('//div[@id="intro"]/p/text()').extract()
        details = [i.replace(' ','').replace('\n','').replace('\u3000','') for i in details]
        item['details'] = [i for i in details if len(i)>0]                              #小说简介
        urls = response.xpath('//div[@class="listmain"]/dl//dd/a/@href').extract()
        total_page= len(urls)-5
        count = 1
        for base_url in urls[6:]:
            item['seq']= '{}/{}'.format(count,total_page)                               #标识符：当前页数/总页数方便后续处理
            count += 1
            url = 'https://www.zwydw.com'+base_url
            item['url'] = url                                                           #爬取网址方便后续去重所用
            yield scrapy.Request(url,callback=self.parse_item,priority=6,
                                 meta={'item':deepcopy(item),'download_timeout':10})

    def parse_item(self, response):
        item = response.meta['item']
        item['chapter'] = response.xpath('//div[@class="content"]/h1/text()').extract_first()   #章节名称
        text_list = response.xpath('//div[@id="content"]//text()').extract()
        text_list = [i.replace('\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0','').replace('\r','') for i in text_list]
        text_list= [i for i in text_list if len(i)>0]
        text = ''.join(text_list[0:-2])
        item['text'] =text                                                                      #正文内容
        yield item
