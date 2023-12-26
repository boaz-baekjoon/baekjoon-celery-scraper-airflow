import logging

import scrapy
import pandas as pd
from baekjoon_scraper.config import config
import json

from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
from baekjoon_scraper.items import UserResultItem
import redis


class UserResultPullScraperSpider(scrapy.Spider):
    name = 'user_result_pull_scraper'
    allowed_domains = ["www.acmicpc.net"]
    redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_DELAY': 0,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'CONCURRENT_REQUESTS': 32,
        'HTTPCACHE_ENABLED': True
    }

    def start_requests(self):

        while True:
            user_page_url = self.redis_client.rpop('user_result_page_url')
            if not user_page_url:
                break

            user_page_url = user_page_url.decode('utf-8')

            yield scrapy.Request(user_page_url, meta={
                'user_id': user_page_url.split('/')[-1],
                # 'proxy': self.get_proxy()
            })

    def parse(self, response):
        user_id = response.meta['user_id']
        problem_table = response.css('div.panel.panel-default')
        ac, wa, tle = [], [], []
        interested_titles = {'맞은 문제': ac, '맞았지만 만점을 받지 못한 문제': wa, '시도했지만 맞지 못한 문제': tle}

        for each_table in problem_table:
            table_title = each_table.css('h3::text').get()
            if table_title not in interested_titles.keys():
                continue

            et = each_table.css('div.problem-list a::text').getall()
            interested_titles[table_title].extend(et)

        yield UserResultItem(
            user_id=user_id, correct_answer=ac, answer_not_perfect=wa, try_not_correct=tle
        )

    def _get_user_id(self):
        """Fetches user_id and user_rank from the database."""
        try:
            engine = self.init_db()
            Session = sessionmaker(bind=engine)
            session = Session()

            metadata = MetaData()
            metadata.reflect(engine)
            users_table = metadata.tables['users']

            # Query the database for user_id and user_rank, sorting by user_rank
            query = session.query(
                users_table.c.user_id,
                users_table.c.user_rank
            ).order_by(users_table.c.user_rank)

            user_info = [
                {'user_id': row.user_id, 'user_rank': row.user_rank}
                for row in query.all()
            ]

            return user_info

        except Exception as e:
            logging.error(f"Database query error: {e}")
            return []

        finally:
            session.close()
            engine.dispose()

    @staticmethod
    def init_db():
        username = config.DB_USER
        password = config.DB_PASSWORD
        host = config.DB_HOST
        port = config.DB_PORT
        database = config.DB_NAME
        engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

        return engine

    @staticmethod
    def get_proxy():
        proxy_ip = config.PROXY_SERVER_IP
        return proxy_ip
