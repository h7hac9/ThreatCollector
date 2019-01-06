# -*- coding: utf-8 -*-
import scrapy


class BadipsSpider(scrapy.Spider):
    name = 'badips'
    allowed_domains = ['badips.com']
    start_urls = ['https://www.badips.com/info']

    def parse(self, response):
        uris = response.css().css("a").xpath("@href").extract()
        pass
