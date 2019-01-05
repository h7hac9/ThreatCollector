# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser

import scrapy

from ThreatCollector.items import HostsFileItem


class HostsFileSpider(scrapy.Spider):
    name = 'hosts-file'
    allowed_domains = ['hosts-file.net']
    start_urls = ['https://hosts-file.net/rss.asp']

    def parse(self, response):
        # 使用RSS文件解析
        last_build = response.css("channel lastBuildDate::text").extract()[0]

        conf = ConfigParser()
        conf.read("crawl.ini")
        last_last_build = conf.get(self.name, "last_build")

        if last_last_build != last_build:
            conf.set(self.name, "last_build", last_build)
            for message_line in response.css("channel item"):
                host_file_item = HostsFileItem()
                host_file_item['host_name'] = message_line.css("title::text").extract()[0]
                host_file_item['link'] = message_line.css("link::text").extract()[0]
                description = message_line.css("description::text").extract()[0]
                elements = description.split("<br>")
                host_file_item["ip"] = elements[1].split(":")[1].strip(" ")
                host_file_item["host_class"] = elements[2].split(":")[1].strip(" ")
                host_file_item["add_time"] = message_line.css("pubDate::text").extract()[0]
                host_file_item["last_build"] = last_build

                yield host_file_item
