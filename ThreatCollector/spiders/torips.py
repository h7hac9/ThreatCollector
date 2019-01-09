# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from ConfigParser import ConfigParser

from ThreatCollector.items import TorIpItem


class ToripsSpider(scrapy.Spider):
    name = 'torips'
    allowed_domains = ['dan.me.uk']
    start_urls = ['https://www.dan.me.uk/torlist/']

    config = ConfigParser()
    config.read("scrapy.cfg")

    def parse(self, response):

        last_ip = self.config.get(self.name, "last_ip")
        tor_ips = response.body.split("\n")

        if last_ip == "":
            end_station = len(tor_ips)

        elif last_ip in tor_ips:
            end_station = len(tor_ips.index(last_ip))

        else:
            end_station = 1
            pass

        for ip in tor_ips[:end_station]:
            tor_ip = TorIpItem()
            tor_ip["ip"] = ip.strip("\n")
            tor_ip["add_time"] = datetime.utcnow()
            yield tor_ip

        self.config.set(self.name, "last_ip", tor_ips[0])
        self.config.write(open("scrapy.cfg", "w+"))
