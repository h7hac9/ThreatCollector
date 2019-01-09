# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from ConfigParser import ConfigParser

from ThreatCollector.items import RansomwaretrackerItem
from ThreatCollector.Libraries.threat_email import ThreatEmail


class RansomwaretrackerSpider(scrapy.Spider):
    name = 'ransomwaretracker'
    allowed_domains = ['ransomwaretracker.abuse.ch']
    start_urls = ['https://ransomwaretracker.abuse.ch/feeds/csv/']

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

        yield scrapy.Request(url='https://ransomwaretracker.abuse.ch/feeds/csv/', callback=self.parse)

    def parse(self, response):

        last_time = self.config.get(self.name, "last_time")

        print response.body.split("\n")[9].replace("\"","").split(",")[0]

        if last_time != response.body.split("\n")[9].replace("\"","").split(",")[0]:

            self.config.set(self.name, "last_time", response.body.split("\n")[9].replace("\"","").split(",")[0])
            self.config.write(open("scrapy.cfg", "w+"))

            for line in response.body.split("\n"):

                if line.startswith("#") is not True:
                    record = line.replace("\"", "").split(",")
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

    def close(spider, reason):
        end = datetime.now()

        email_message = "The {} start at {}, and end at {}".format(spider.name, spider.start, end)

        threat_email = ThreatEmail()
        threat_email.send_mail(spider.config.get("email_service", "user_name"),
                               spider.config.get("email_service", "receivers"),
                               "{} spider information".format(spider.name),
                               email_message)
