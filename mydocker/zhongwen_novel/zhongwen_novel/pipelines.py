# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from redis import StrictRedis


class ZhongwenNovelPipeline(object):


    def open_spider(self, spider):
        '''连接mongodb和redis'''
        host = spider.settings.get('MONGO_HOST')
        port = spider.settings.get('MONGO_PORT')
        user = spider.settings.get('MONGO_USER')
        password= spider.settings.get('MONGO_PASSWORD')
        self.client = MongoClient(host, port)
        self.client.admin.authenticate(user, password, mechanism='SCRAM-SHA-1')
        self.db = self.client['novel']

        rhost = spider.settings.get('REDIS_HOST')
        rport = spider.settings.get('REDIS_PORT')
        rdb = spider.settings.get('REDIS_INDEX')
        rpassword = spider.settings.get('REDIS_PASSWORD')
        self.redis_coon = StrictRedis(host=rhost, port=rport, db=rdb, password=rpassword, decode_responses=True)

    def process_item(self, item, spider):
        table = item['title']
        data = item['url']
        db_coon = self.db[table]

        try:
            if db_coon.insert_one(item):
                self.redis_coon.sadd('{}finish_url'.format(table),data)
                print('{}----{}成功存储到MongoDB'.format(item['title'],item['chapter']))
        except Exception as e:
            print('{}----{}存储失败'.format(item['title'],item['chapter']),e)
        return item

    def close_spider(self, spider):
        self.client.close()
        self.redis_coon.close()

