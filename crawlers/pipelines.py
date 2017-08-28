# -*- coding: utf-8 -*-

import pymongo
import os
import re

OUTPUT_DIR = 'data'


class MatchReportPipeline(object):

    def process_item(self, item, spider):
        """
        Construct path and save.
        :param item: items.MatchReport
        :param spider: squawka.SquawkaSpider
        :return: items.MatchReport
        """
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        competition = re.findall("s3-irl-(.*)\.squawka\.com", item['url'])
        game_id = re.findall("ingame/(.*)", item['url'])
        file_name = '_'.join((competition[0], game_id[0])) + '.xml'
        item_path = os.sep.join((OUTPUT_DIR, file_name))
        with open(item_path, 'wr') as f:
            f.write(item['data'])
        return item


class MongoPipeline(object):
    collection_name = 'squawka'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'squawka')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
