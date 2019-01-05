# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import re

from ThreatCollector.items import PhishtankItem

class PhishtankSpider(scrapy.Spider):
    name = 'phishtank'
    allowed_domains = ['phishtank.com']
    start_urls = ['https://phishtank.com/phish_search.php?verified=u&active=y']

    def parse(self, response):
        short_urls = response.css("tr td a").xpath("@href").extract()
        for short_url in short_urls:
            if "phish_id" in short_url:
                yield scrapy.Request(response.urljoin(short_url), callback=self.detailed_parse)

        if len(response.css("td b a").xpath("@href").extract()) > 1:
            next_right_short_url = response.css("td b a").xpath("@href").extract()[1]
            yield scrapy.Request(response.urljoin(next_right_short_url), callback=self.parse)
        else:
            next_short_url = response.css("td b a").xpath("@href").extract_first()
            yield scrapy.Request(response.urljoin(next_short_url), callback=self.parse)

    def detailed_parse(self, response):
        print "================>[crawl] {}<===============".format(response.url)
        phishtank = PhishtankItem()
        phishtank["phishing_site"] = response.css("div span b::text").extract_first()
        phishtank["add_time"] = datetime.utcnow()

        submit_time = response.css("div.url span.small::text").extract()[1]
        result = re.match(r'(.*): (?P<submit_time>.*)\)(.*)', submit_time)
        submit_time = result.groupdict().get("submit_time")

        phishtank["status"] = response.css("div.padded span::text").extract_first().split(" ")[2]

        phishtank["submit_time"] = submit_time

        yield phishtank
