# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime

from ThreatCollector.items import BadipsItem


class BadipsSpider(scrapy.Spider):
    name = 'badips'
    allowed_domains = ['badips.com']
    start_urls = ['https://www.badips.com/info']

    def parse(self, response):
        uris = response.css("div#content a").xpath("@href").extract()

        for uri in uris[2:len(uris)-1]:
            yield scrapy.Request(response.urljoin(uri.strip("\n")), callback=self.detailed_parse)

        next_uri = response.css("p.badips a.badips").xpath("@href").extract_first()
        yield scrapy.Request(response.urljoin(next_uri.strip("\n")), callback=self.next_page_parse)

    def detailed_parse(self, response):
        bad_ip = BadipsItem()
        bad_ip["ip"] = response.css("div.overview-info p.badips b::text").extract_first()
        bad_ip["category"] = response.css("div.overview-info p.badips a.badips::text").extract_first()
        bad_ip["score"] = response.css("div.overview-info p.badips a.badips::text").extract()[1]
        bad_ip["located"] = response.css("div.overview-info p.badips a.badips::text").extract()[3]

        message = response.css("div.overview-info p.badips::text").extract()[-1]
        result = re.search(r'(.*)\son\s(?P<submit_time>.*)\.', message)

        bad_ip["submit_time"] = result.groupdict().get("submit_time")
        bad_ip["add_time"] = datetime.utcnow()

        return bad_ip

    def next_page_parse(self, response):
        uris = response.css("div#content a").xpath("@href").extract()
        for uri in uris:
            yield scrapy.Request(url=response.urljoin(uri.strip("\n")), callback=self.detailed_parse)

        next = response.css("div#content>p.badips>a::text").extract()
        if "next page>" in next:
            next_list_index = next.index("next page>")
            next_uri = response.css("div#content>p.badips>a").xpath("@href").extract()[next_list_index]
            scrapy.Request(next_uri, callback=self.next_page_parse)
