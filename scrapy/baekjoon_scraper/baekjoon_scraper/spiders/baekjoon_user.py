import random
import scrapy
from baekjoon_scraper.spiders.base_spider import BaseSpider
from bs4 import BeautifulSoup
from baekjoon_scraper.items import UserItem
from baekjoon_scraper.config import config
import time
import logging

logger = logging.getLogger('baekjoon_user')
logger.setLevel(logging.INFO)

class BaekjoonUserSpider(BaseSpider):
    '''
    scrapy genspider baekjoon_user www.acmicpc.net/ranklist
    scrapy crawl baekjoon_user -a start=1 -a end=290

    '''
    name = "baekjoon_user"
    allowed_domains = ['www.acmicpc.net']
    proxies = [
        config.PROXY_SERVER_IP
    ]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        # 'FEEDS': {
        #     'bj_users.csv': {
        #         'format': 'csv',
        #         'encoding': 'utf8',
        #         'store_empty': False,
        #         'fields': ['user_rank', 'user_id', 'status_message',
        #                     'user_answer_num', 'user_submit_num',
        #                     'user_answer_rate'],
        #         'overwrite': True,
        #     },
        # },
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False
    }

    def __init__(self, *args, **kwargs):
        super(BaekjoonUserSpider, self).__init__(*args, **kwargs)
        self.start_time = time.time()

    def start_requests(self):
        logger.info("start crawl")
        base_url = 'https://www.acmicpc.net/ranklist/'
        # proxy = random.choice(self.proxies)
        for p_index in range(1, 1200):
            url = base_url + str(p_index)
            # logger.info(url)
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                # meta={'proxy': proxy},
                errback=self.handle_error,
                priority=p_index
            )


    def parse(self, response: scrapy.http.Response):
        rows = response.xpath('//*[@id="ranklist"]/tbody/tr')

        for row in rows:
            cols = row.xpath('td').xpath('string(.)').getall()

            item = UserItem()
            item['user_rank'] = int(cols[0])
            item['user_id'] = cols[1]
            item['status_message'] = cols[2]
            item['user_answer_num'] = int(cols[3])
            item['user_submit_num'] = int(cols[4])
            item['user_answer_rate'] = float(cols[5].strip('%'))
            yield item

    def closed(self, reason):
        end_time = time.time()  # Record end time
        total_time = end_time - self.start_time
        logging.info(f"Spider run time: {total_time:.2f} seconds")

    def handle_error(self, failure):
        # this will log the failure
        self.logger.error(repr(failure))