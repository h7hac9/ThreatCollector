# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from ConfigParser import ConfigParser

from ThreatCollector.items import OpenphishItem


class OpenphishSpider(scrapy.Spider):
    name = 'openphish'
    allowed_domains = ['www.openphish.com']
    start_urls = ['http://www.openphish.com/feed.txt']

    config = ConfigParser()
    config.read("scrapy.cfg")

    def parse(self, response):

        last_url = self.config.get(self.name, "last_url")
        target_urls = response.body.strip("\n").split("\n")

        if last_url == "" or last_url not in target_urls:
            target_index = len(target_urls)

        else:
            target_index = target_urls.index(last_url)

        for url in target_urls[:target_index]:
            openphish_message = OpenphishItem()
            openphish_message["url"] = url
            openphish_message["add_time"] = datetime.utcnow()
            yield openphish_message
