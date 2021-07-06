# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time

import redis
from redis import StrictRedis
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.xlib.pydispatch import dispatcher
from fake_useragent import UserAgent
from scrapy.exceptions import  IgnoreRequest

class ZhongwenNovelSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ZhongwenNovelDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class FilterUrlDownloaderMiddleware(object):
    '''下载链接保存过滤去重'''

    def __init__(self):
        dispatcher.connect(self.spider_closed,signals.spider_closed)


    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        '''对请求的网址进行过滤并添加代理'''
        if request.meta.get('item') == None:
            title = '目录'
            self.redis_coon.sadd(title, request.url)
        else:
            title = request.meta.get('item').get('title')
            self.redis_coon.sadd('{}all_url'.format(title),request.url) #把所有的url都添加到集合总

        if self.redis_coon.sismember('{}finish_url'.format(title),request.url): #再finish集合总查询是否已经爬取过的连接，如果是则丢弃请求
            raise IgnoreRequest
        else:
            while True:
                proxy = self.redis_coon.srandmember('ip')   #通过redis获取代理并添加至requeset中。
                if proxy is not None:
                    break
                print('无可用代理')
                time.sleep(10)
            request.meta['proxy'] = proxy
            print('添加代理：', proxy)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        '''对代理失效和代理超时的异常进行更换代理重新请求'''
        if '10060' in str(exception) or '10061' in str(exception) or'timeout' in str(exception):
            print('{}代理失效,移除代理'.format(request.meta['proxy']))
            self.redis_coon.srem('ip', request.meta['proxy'])
            proxy = self.redis_coon.srandmember('ip')
            request.meta['proxy'] = proxy
            request.dont_filter = True
            return request
        return None

    def spider_opened(self, spider):
        '''爬虫启动时连接redis数据库'''
        spider.logger.info('Spider opened: %s' % spider.name)
        host = spider.settings.get('REDIS_HOST')
        port = spider.settings.get('REDIS_PORT')
        password = spider.settings.get('REDIS_PASSWORD')
        db = spider.settings.get('REDIS_INDEX')
        self.redis_coon=StrictRedis(host, port, db, password,decode_responses=True)
        print('redis数据库链接成功')

    def spider_closed(self, spider):
        '''关闭爬虫时把所有待爬取连接保存起来，并断开redis数据库'''
        spider.logger.info('Spider closed:%s' % spider.name)
        for i in self.redis_coon.keys():
            if 'all' in i:
                title = i.split('all')[0]
                print(title)
                self.redis_coon.sdiffstore('{}new_url'.format(title), '{}all_url'.format(title), '{}finish_url'.format(title))
        self.redis_coon.close()
        print('redis数据库关闭')
