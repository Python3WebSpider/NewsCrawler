# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


class PgSQLPipeline():
    def process_item(self, item, spider):
        try:
            item.save()
        except IntegrityError:
            logger.info('《%s》of %s already exists', item.get('title'), item.get('website'))
        return item
