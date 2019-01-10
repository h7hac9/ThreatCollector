# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from ConfigParser import ConfigParser

from ThreatCollector.items import TorIpItem
from ThreatCollector.Libraries.threat_email import ThreatEmail


class ToripsSpider(scrapy.Spider):
    name = 'torips'
    allowed_domains = ['dan.me.uk']
    start_urls = ['https://www.dan.me.uk/torlist/']

    config = ConfigParser()
    config.read("scrapy.cfg")

    def start_requests(self):
        self.start = datetime.now()

        email_message = "The {} start at {}".format(self.name, self.start)

        threat_email = ThreatEmail()
        threat_email.send_mail(self.config.get("email_service", "user_name"),
                               self.config.get("email_service", "receivers"),
                               "{} spider information".format(self.name),
                               email_message)

        yield scrapy.Request(url='https://www.dan.me.uk/torlist/', callback=self.parse)

    def parse(self, response):

        last_ip = self.config.get(self.name, "last_ip")
        tor_ips = response.body.split("\n")

        if last_ip == "":
            end_station = len(tor_ips)

        elif last_ip in tor_ips:
            end_station = tor_ips.index(last_ip)+1

        else:
            end_station = 0

        for ip in tor_ips[:end_station]:
            tor_ip = TorIpItem()
            tor_ip["ip"] = ip.strip("\n")
            tor_ip["add_time"] = datetime.utcnow()
            yield tor_ip

        self.config.set(self.name, "last_ip", tor_ips[0])
        self.config.write(open("scrapy.cfg", "w+"))

    def close(spider, reason):
        end = datetime.now()

        email_message = "The {} start at {}, and end at {}".format(spider.name, spider.start, end)

        threat_email = ThreatEmail()
        threat_email.send_mail(spider.config.get("email_service", "user_name"),
                               spider.config.get("email_service", "receivers"),
                               "{} spider information".format(spider.name),
                               email_message)
