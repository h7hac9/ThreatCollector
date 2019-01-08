# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime
from ConfigParser import ConfigParser

from ThreatCollector.items import BadipsItem


class BadipsSpider(scrapy.Spider):
    name = 'badips'
    allowed_domains = ['badips.com']
    start_urls = ['https://www.badips.com/info']

    conf = ConfigParser()
    conf.read("scrapy.cfg")

    queue_set = []

    def parse(self, response):
        uris = response.css("div#content a").xpath("@href").extract()

        last_id = self.conf.get(self.name, "last_id")

        ids = response.css("div#content a::text").extract()

        if last_id == "":
            end_locate = len(uris)-1
            self.conf.set(self.name, "last_id", ids[1].strip("\n"))
            self.conf.write(open("scrapy.cfg","w+"))
            next = response.css("div#content>p.badips>a::text").extract()
            if "next page>" in next:
                next_list_index = next.index("next page>")
                next_uri = response.css("div#content>p.badips>a").xpath("@href").extract()[next_list_index]
                yield scrapy.Request(next_uri, callback=self.next_page_parse)
        else:
            self.queue_set.append(ids[1])
            if last_id+"\n" in ids[1:len(ids)-1]:
                self.conf.set(self.name, "last_id", self.queue_set[0])
                self.conf.write(open("scrapy.cfg", "w+"))
                end_locate = ids.index(last_id+"\n")
                self.conf.set(self.name, "last_id", last_id)

            else:
                end_locate = len(uris)-1
                next = response.css("div#content>p.badips>a::text").extract()

                if "next page>" in next:
                    next_list_index = next.index("next page>")
                    next_uri = response.css("div#content>p.badips>a").xpath("@href").extract()[next_list_index]
                    yield scrapy.Request(next_uri, callback=self.parse)

        for uri in uris[1:end_locate]:
            yield scrapy.Request(response.urljoin(uri.strip("\n")), callback=self.detailed_parse)

    def detailed_parse(self, response):
        bad_ip = BadipsItem()
        bad_ip["ip"] = response.css("div.overview-info p.badips b::text").extract_first()

        category_list = response.css("div.overview-info ul li a::text").extract()
        if len(category_list) != 0:
            categorys = self.handle_arrays(category_list)
            bad_ip["category"] = categorys
            bad_ip["located"] = response.css("div.overview-info p.badips a.badips::text").extract()[0]
        else:
            bad_ip["category"] = response.css("div.overview-info p.badips a.badips::text").extract_first()
            bad_ip["located"] = response.css("div.overview-info p.badips a.badips::text").extract()[2]

        bad_ip["score"] = response.css("div.overview-info p.badips a.badips::text").extract()[1]

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
            yield scrapy.Request(next_uri, callback=self.next_page_parse)

    def handle_arrays(self, src_list):

        dst_list = []

        for subscript in xrange(len(src_list)):
            if subscript % 2 == 0:
                dst_list.append(src_list[subscript])

        return dst_list
