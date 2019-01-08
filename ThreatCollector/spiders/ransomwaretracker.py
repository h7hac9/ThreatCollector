# -*- coding: utf-8 -*-
import scrapy


class RansomwaretrackerSpider(scrapy.Spider):
    name = 'ransomwaretracker'
    allowed_domains = ['ansomwaretracker.abuse.ch']
    start_urls = ['http://ansomwaretracker.abuse.ch/']

    def parse(self, response):
        for line in response.body.split("\n"):
            if line.startswith("#") is not True:
                pass
        pass
