# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

import ThreatCollector.settings as setting


class ThreatcollectorPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoDBPipeline(object):
    def __init__(self):
        host = setting.MONGODB_HOST
        port = setting.MONGODB_PORT
        db_name = setting.MONGODB_DBNAME
        client = pymongo.MongoClient(host=host, port=port)

        self.db = client[db_name]

    def process_item(self, item, spider):

        table = self.db[spider.name]

        if spider.name == "hosts-file":
            table.ensure_index("host_name")

        if spider.name == "blocklist-de":
            table.ensure_index("ip")

        quote_into = dict(item)
        table.insert(quote_into)
        return item
