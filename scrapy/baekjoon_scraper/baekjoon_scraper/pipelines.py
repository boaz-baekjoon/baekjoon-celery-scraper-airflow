# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from collections import defaultdict
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
import polars as pl
from baekjoon_scraper.config import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
import pandas as pd
import logging


class RDSFullRefreshPipeline:
    def __init__(self):
        self.items = defaultdict(list)
        self.engine = None

    def open_spider(self, spider):
        logging.warning('open_spider - pipeline')
        self.engine = self.init_db()
        logging.warning('open_spider - pipeline - db engine connected')

    def close_spider(self, spider):
        logging.warning('close_spider - pipeline')
        df = None
        table_name = None
        for item_type, items in self.items.items():
            if item_type == 'ProblemItem':
                table_name = 'problems'
                sorted_items = sorted(items, key=lambda i: i['problem_id'])
                df = pd.DataFrame(sorted_items)
                df.set_index(['problem_id'], inplace=True)
            elif item_type == 'UserItem':
                table_name = 'users'
                sorted_items = sorted(items, key=lambda i: i['user_rank'])
                df = pd.DataFrame(sorted_items)
                df.set_index(['user_id'], inplace=True)
            elif item_type == 'WorkbookItem':
                table_name = 'workbooks'
                sorted_items = sorted(items, key=lambda i: i['workbook_rank'])
                df = pd.DataFrame(sorted_items)
                df.set_index(['workbook_id', 'problem_id'], inplace=True)
            else:
                sorted_items = items

            try:
                df.to_sql(table_name, con=self.engine, if_exists='replace', index=True)
                logging.warning(f'close_spider - pipeline - {table_name} table created')
            except Exception as e:
                logging.warning(f'close_spider - pipeline - {table_name} table creation failed')
                logging.warning(e)

        if self.engine:
            self.engine.dispose()
            logging.warning('close_spider - pipeline - db engine disconnected')

    def process_item(self, item, spider):
        item_type = type(item).__name__
        self.items[item_type].append(item)
        return item

    @staticmethod
    def init_db():
        username = config.DB_USER
        password = config.DB_PASSWORD
        host = config.DB_HOST
        port = config.DB_PORT
        database = config.DB_NAME
        engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

        return engine

