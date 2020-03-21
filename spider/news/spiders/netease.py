# -*- coding: utf-8 -*-
import json
from random import random
import dateparser
import pytz
from scrapy import Request, Spider
from spider.news.items import NewsItem
import hashlib


class NeteaseSpider(Spider):
    name = 'netease'
    allowed_domains = ['news.163.com']
    tz = pytz.timezone('Asia/Shanghai')

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,zh-TW;q=0.6,mt;q=0.5',
    }

    def start_requests(self):
        url = 'http://news.163.com/special/0001220O/news_json.js?' + str(random())
        yield Request(url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        data = response.body.decode('gbk')
        data = data[9:-1]
        data = json.loads(data)
        for group in data.get('news'):
            for item in group:
                news = NewsItem({
                    'code': hashlib.md5(item.get('l').encode('utf-8')).hexdigest(),
                    'title': item.get('t'),
                    'url': item.get('l'),
                    'published_at': self.tz.localize(dateparser.parse(item.get('p'))),
                    'source': '网易新闻',
                    'website': '网易新闻',
                    'domain': 'news.163.com',
                    'thumb': None
                })
                yield news
