# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from ConfigParser import ConfigParser

from ThreatCollector.items import RansomwaretrackerItem


class RansomwaretrackerSpider(scrapy.Spider):
    name = 'ransomwaretracker'
    allowed_domains = ['ansomwaretracker.abuse.ch']
    start_urls = ['http://ansomwaretracker.abuse.ch/']

    config = ConfigParser()
    config.read("scrapy.cfg")

    def parse(self, response):

        last_time = self.config.get(self.name, "last_time")
        if last_time != response.body.split("\n")[9].split(",")[1]:

            for line in response.body.split("\n"):

                if line.startswith("#") is not True:
                    record = line.split(",")
                    ransomitem = RansomwaretrackerItem()
                    ransomitem["submit_time"] = record[0]
                    ransomitem["threat"] = record[1]
                    ransomitem["malware"] = record[2]
                    ransomitem["host"] = record[3]
                    ransomitem["url"] = record[4]
                    ransomitem["status"] = record[5]
                    ransomitem["register"] = record[6]
                    ransomitem["ip"] = record[7]
                    ransomitem["asn"] = record[8]
                    ransomitem["country"] = record[9]
                    ransomitem["add_time"] = datetime.utcnow()
                    yield ransomitem
            self.config.set(self.name, "last_time", response.body.split("\n")[9].split(",")[1])
            self.config.write(open("scrapy.cfg", "w+"))
