import random
import scrapy
from baekjoon_scraper.spiders.base_spider import BaseSpider
from bs4 import BeautifulSoup
from baekjoon_scraper.items import ProblemItem
from baekjoon_scraper.config import config
import time
import logging

logger = logging.getLogger('baekjoon_problem')
logger.setLevel(logging.INFO)


class ProblemsetSpider(BaseSpider):
    '''
    scrapy startproject problemset
    scrapy crawl problemset
    scrapy crawl problemset
    '''
    name = "baekjoon_problem"
    allowed_domains = ["www.acmicpc.net"]
    proxies = [
        config.PROXY_SERVER_IP
    ]
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        # 'FEEDS': {
        #     'problems.csv': {
        #         'format': 'csv',
        #         'encoding': 'utf8',
        #         'store_empty': False,
        #         'fields': ['problem_id', 'problem_title', 'problem_info', 'problem_answer_num', 'problem_submit_num',
        #                    'problem_answer_rate'],
        #         'overwrite': True,
        #     },
        # },
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False
    }

    def __init__(self, *args, **kwargs):
        super(ProblemsetSpider, self).__init__(*args, **kwargs)
        self.start_time = time.time()
        logging.getLogger('scrapy.core.scraper').setLevel(logging.WARNING)

    def start_requests(self):
        first_page_url = "https://www.acmicpc.net/problemset/1"
        for p_index in range(1, 290):
            proxy = random.choice(self.proxies)
            yield scrapy.Request(
                url=first_page_url,
                callback=self.parse,
                meta={'proxy': proxy, 'page_number': 1},
                errback=self.handle_error
            )

    def parse(self, response: scrapy.http.Response):
        rows = response.xpath('//*[@id="problemset"]/tbody/tr')
        for row in rows:
            cols = row.xpath('td').xpath('string(.)').getall()
            cols = [col.strip() for col in cols]

            item = ProblemItem()
            item['problem_id'] = int(cols[0])
            item['problem_title'] = cols[1]
            item['problem_info'] = cols[2]
            item['problem_answer_num'] = int(cols[3])
            item['problem_submit_num'] = int(cols[4])
            item['problem_answer_rate'] = float(cols[5].strip('%'))

            yield item

        current_page = response.meta['page_number']
        if current_page < 289:
            next_page_url = f"https://www.acmicpc.net/problemset/{current_page + 1}"
            proxy = random.choice(self.proxies)
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={'proxy': proxy, 'page_number': current_page + 1},
                errback=self.handle_error
            )

    def closed(self, reason):
        end_time = time.time()  # Record end time
        total_time = end_time - self.start_time
        logging.info(f"Spider run time: {total_time:.2f} seconds")

    def handle_error(self, failure):
        # this will log the failure
        self.logger.error(repr(failure))
