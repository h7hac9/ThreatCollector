# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from ConfigParser import ConfigParser


class ThreatEmail(object):

    config = ConfigParser()
    config.read("scrapy.cfg")

    sender = config.get("email_service", "user_name")
    receivers = config.get("email_service", "receivers").split(";")

    def send_mail(self, from_user, to_user, subject, email_message):
        message = MIMEText(email_message, "plain", "utf-8")
        message['From'] = from_user
        message['To'] = to_user
        message['Subject'] = Header(subject, 'utf-8')

        try:
            host = self.config.get("email_service", "host")
            port = self.config.get("email_service", "port")
            user_name = self.config.get("email_service", "user_name")
            password = self.config.get("email_service", "password")
            smtpObj = smtplib.SMTP_SSL(host,port)
            smtpObj.login(user_name, password)
            smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            smtpObj.close()
            print "邮件发送成功"
        except smtplib.SMTPException:
            print "Error: 无法发送邮件"

