# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import re
from ConfigParser import ConfigParser

from ThreatCollector.items import PhishtankItem


class PhishtankSpider(scrapy.Spider):
    name = 'phishtank'
    allowed_domains = ['phishtank.com']
    start_urls = ['http://phishtank.com/phish_archive.php']

    config = ConfigParser()
    config.read("scrapy.cfg")

    config_new_id = "0"

    def parse(self, response):
        last_id = response.css("tr td a::text").extract_first()
        short_urls = response.css("tr td a").xpath("@href").extract()
        find_id = self.config.get(self.name, "last_id")

        if find_id == "":

            self.config.set(self.name, "last_id", last_id)
            self.config.write(open("scrapy.cfg", "w+"))

            for short_url in short_urls:
                if "phish_id" in short_url:
                    yield scrapy.Request(response.urljoin(short_url), callback=self.detailed_parse)

            next_right_short_url = response.css("td b a").xpath("@href").extract_first()
            yield scrapy.Request(response.urljoin(next_right_short_url), callback=self.next_page_parse)

        elif find_id != last_id:

            if "phish_detail.php?phish_id="+find_id in short_urls:
                last_index = short_urls.index("phish_detail.php?phish_id="+find_id)
                self.config.set(self.name, "last_id", self.config_new_id)
                self.config.write(open("scrapy.cfg", "w+"))

            else:
                last_index = len(short_urls)
                if len(response.css("td b a").xpath("@href").extract()) > 1:
                    next_right_short_url = response.css("td b a").xpath("@href").extract()[1]
                    yield scrapy.Request(response.urljoin(next_right_short_url), callback=self.parse)
                else:
                    next_short_url = response.css("td b a").xpath("@href").extract_first()
                    yield scrapy.Request(response.urljoin(next_short_url), callback=self.parse)

            if int(last_id) > int(self.config_new_id):
                self.config_new_id = last_id

            for short_url in short_urls[:last_index]:
                if "phish_id" in short_url:
                    yield scrapy.Request(response.urljoin(short_url), callback=self.detailed_parse)

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

    def next_page_parse(self, response):
        short_urls = response.css("tr td a").xpath("@href").extract()

        for short_url in short_urls:
            if "phish_id" in short_url:
                yield scrapy.Request(response.urljoin(short_url), callback=self.detailed_parse)

        next_right_short_url = response.css("td b a").xpath("@href").extract()[1]
        yield scrapy.Request(response.urljoin(next_right_short_url), callback=self.next_page_parse)
