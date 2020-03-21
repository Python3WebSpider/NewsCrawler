# -*- coding: utf-8 -*-
import datetime
from scrapy import Request, Spider
import json
from spider.news.items import NewsItem


class SinaSpider(Spider):
    name = 'sina'
    allowed_domains = ['sina.com.cn']
    start_urls = ['http://sina.com.cn/']
    index_url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page={page}'

    def start_requests(self):
        for page in range(1, 51):
            url = self.index_url.format(page=page)
            yield Request(url, self.parse)

    def parse(self, response):
        data = json.loads(response.text)
        for item in data.get('result', {}).get('data'):
            news = NewsItem({
                'code': item.get('oid'),
                'title': item.get('title'),
                'url': item.get('url'),
                'published_at': datetime.datetime.fromtimestamp(int(item.get('ctime'))),
                'source': item.get('环球网'),
                'website': '新浪新闻',
                'domain': 'news.sina.com.cn',
                'thumb': (item.get('images') or [{}])[0].get('u')
            })
            yield news
