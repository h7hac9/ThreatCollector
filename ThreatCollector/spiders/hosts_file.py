# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from datetime import datetime

import scrapy

from ThreatCollector.items import HostsFileItem
from ThreatCollector.Libraries.threat_email import ThreatEmail


class HostsFileSpider(scrapy.Spider):
    name = 'hosts-file'
    allowed_domains = ['hosts-file.net']
    start_urls = ['https://hosts-file.net/rss.asp']

    def start_requests(self):
        self.start = datetime.now()

        email_message = "The {} start at {}".format(self.name, self.start)

        threat_email = ThreatEmail()
        threat_email.send_mail(self.name, "administrator", "{} spider information".format(self.name), email_message)

        yield scrapy.Request(url='https://hosts-file.net/rss.asp', callback=self.parse)

    def parse(self, response):
        # 使用RSS文件解析
        last_build = response.css("channel lastBuildDate::text").extract()[0]

        conf = ConfigParser()
        conf.read("scrapy.cfg")
        last_last_build = conf.get(self.name, "last_build")

        now = datetime.utcnow()

        if last_last_build != last_build:
            conf.set(self.name, "last_build", last_build)
            conf.write(open("scrapy.cfg", "w+"))

            for message_line in response.css("channel item"):
                host_file_item = HostsFileItem()
                host_file_item['host_name'] = message_line.css("title::text").extract()[0]
                host_file_item['link'] = message_line.css("link::text").extract()[0]
                description = message_line.css("description::text").extract()[0]
                elements = description.split("<br>")
                host_file_item["ip"] = elements[1].split(":")[1].strip(" ")
                host_file_item["host_class"] = elements[2].split(":")[1].strip(" ")
                host_file_item["submit_time"] = message_line.css("pubDate::text").extract()[0]
                host_file_item["last_build"] = last_build
                host_file_item["add_time"] = now

                yield host_file_item

        print "========>Synchronization Complete<========"

    def close(spider, reason):
        end = datetime.now()

        email_message = "The {} start at {}, and end at {}".format(spider.name, spider.start, end)

        threat_email = ThreatEmail()
        threat_email.send_mail(spider.name, "administrator", "{} spider information".format(spider.name), email_message)
