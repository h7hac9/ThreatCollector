# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime

from ThreatCollector.items import BlockListDEItem


class BlocklistDeSpider(scrapy.Spider):
    name = 'blocklist-de'
    allowed_domains = ['blocklist.de']
    start_urls = ['https://www.blocklist.de/en/export.html']

    def parse(self, response):
        urls = response.css("strong a").xpath("@href").extract()

        for url in urls[1:]:
            yield scrapy.Request(url, callback=self.block_ip_parse)

    def block_ip_parse(self, response):
        re_result = re.match(r'(.*)/(?P<type>.*?)\.txt', response.url)
        ip_type = re_result.groupdict().get("type")

        now = datetime.now().strftime("%a, %d %b %Y %H:%M %Z")

        for ip in response.body.split("\n"):
            block_ip = BlockListDEItem()
            block_ip["ip"] = ip
            block_ip["type"] = ip_type
            block_ip["add_time"] = now
            yield block_ip
