# -*- coding: utf-8 -*-
import scrapy
import re
from datetime import datetime

from ThreatCollector.items import BlockListDEItem
from ThreatCollector.Libraries.threat_email import ThreatEmail


class BlocklistDeSpider(scrapy.Spider):
    name = 'blocklist-de'
    allowed_domains = ['blocklist.de']
    start_urls = ['https://www.blocklist.de/en/export.html']

    def start_requests(self):
        self.start = datetime.now()

        email_message = "The {} start at {}".format(self.name, self.start)

        threat_email = ThreatEmail()
        threat_email.send_mail(self.name, "administrator", "{} spider information".format(self.name), email_message)

        yield scrapy.Request(url='https://www.blocklist.de/en/export.html', callback=self.parse)

    def parse(self, response):
        urls = response.css("strong a").xpath("@href").extract()

        for url in urls[1:]:
            yield scrapy.Request(url, callback=self.block_ip_parse)

    def block_ip_parse(self, response):
        re_result = re.match(r'(.*)/(?P<type>.*?)\.txt', response.url)
        ip_type = re_result.groupdict().get("type")

        now = datetime.utcnow()

        for ip in response.body.split("\n"):
            block_ip = BlockListDEItem()
            block_ip["ip"] = ip
            block_ip["type"] = ip_type
            block_ip["add_time"] = now
            yield block_ip

    def close(spider, reason):
        end = datetime.now()

        email_message = "The {} start at {}, and end at {}".format(spider.name, spider.start, end)

        threat_email = ThreatEmail()
        threat_email.send_mail(spider.name, "administrator", "{} spider information".format(spider.name), email_message)

