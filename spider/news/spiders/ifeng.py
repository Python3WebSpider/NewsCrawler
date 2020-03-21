# -*- coding: utf-8 -*-
from datetime import datetime
from scrapy import Spider, Request
import re
import json
from spider.news.items import NewsItem
import dateparser
import pytz


class IfengSpider(Spider):
    name = 'ifeng'
    allowed_domains = ['news.ifeng.com', 'shankapi.ifeng.com']
    start_urls = ['http://news.ifeng.com/']
    next_url = 'http://shankapi.ifeng.com/shanklist/_/getColumnInfo/_/dynamicFragment/{code}/{timestamp}/20/3-35191-'
    tz = pytz.timezone('Asia/Shanghai')

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_first)

    def parse_data(self, data):
        news_list = data.get('newsstream', [])
        for item in news_list:
            news = NewsItem({
                'code': item.get('id'),
                'title': item.get('title'),
                'url': item.get('url'),
                'published_at': self.tz.localize(dateparser.parse(item.get('newsTime'))),
                'source': item.get('source'),
                'website': '凤凰网',
                'domain': 'news.ifeng.com',
                'thumb': (item.get('thumbnails', {}).get('image') or [{}])[0].get('url')
            })
            yield news

    def parse_first(self, response):
        # define pattern to extract json data from index html page
        pattern = re.compile('allData\s+=(.*?);\s+var\s+adData', re.S)
        result = re.search(pattern, response.text)

        # if no data from index page, just return
        if not result: return

        # load json data
        result = result.group(1)
        data = json.loads(result)

        # parse news from index page
        news = None
        for news in self.parse_data(data):
            if news: yield news

        # next page
        last_news = news or {}
        last_news_code = last_news.get('code')
        timestamp = int(datetime.timestamp(news.get('published_at')) * 1000)
        next_url = self.next_url.format(
            code=last_news_code,
            timestamp=timestamp
        )
        yield Request(next_url, callback=self.parse_next)

    def parse_next(self, response):
        data = json.loads(response.text)

        # get news from data
        news = None
        for news in self.parse_data(data.get('data', {})):
            if news: yield news

        # process next
        is_end = data.get('data', {}).get('isEnd')
        if is_end: return
        # next page
        last_news = news
        last_news_code = last_news.get('code')
        timestamp = int(datetime.timestamp(news.get('published_at')) * 1000)
        next_url = self.next_url.format(
            code=last_news_code,
            timestamp=timestamp
        )
        yield Request(next_url, callback=self.parse_next)
