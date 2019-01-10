# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime

from ThreatCollector.items import GreensnowItem


class GreensnowSpider(scrapy.Spider):
    name = 'greensnow'
    allowed_domains = ['blocklist.greensnow.co']
    start_urls = ['https://blocklist.greensnow.co/greensnow.txt']

    def parse(self, response):

        for i in response.body.strip("\n").split("\n"):
            greensnow_blockip = GreensnowItem()
            greensnow_blockip["ip"] = i
            greensnow_blockip["add_time"] = datetime.utcnow()
            yield greensnow_blockip
