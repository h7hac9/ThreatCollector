# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThreatcollectorItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HostsFileItem(scrapy.Item):
    host_name = scrapy.Field()
    ip = scrapy.Field()
    link = scrapy.Field()
    host_class = scrapy.Field()
    add_time = scrapy.Field()
    last_build = scrapy.Field()


class BlockListDEItem(scrapy.Item):
    ip = scrapy.Field()
    type = scrapy.Field()
    add_time = scrapy.Field()
