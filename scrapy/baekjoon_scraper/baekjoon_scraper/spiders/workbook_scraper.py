from collections import defaultdict

import scrapy

from baekjoon_scraper.config import config
from baekjoon_scraper.spiders.base_spider import BaseSpider
from baekjoon_scraper.items import WorkbookItem
import time
import logging

logger = logging.getLogger('workbook_scraper')
logger.setLevel(logging.INFO)


class WorkbookScraperSpider(BaseSpider):
    name = "workbook_scraper"
    allowed_domains = ["www.acmicpc.net"]
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            'workbooks.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': ['workbook_rank', 'workbook_id', 'user_id',
                           'workbook_title', 'problem_id',
                           'problem_title'],
                'overwrite': True,
            },
        },
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'HTTPERROR_ALLOWED_CODES': [301, 302, 400, 403, 404, 500]
    }

    def __init__(self, start=1, end=20, *args, **kwargs):
        super(WorkbookScraperSpider, self).__init__(*args, **kwargs)
        self.start_time = time.time()
        self.base_url = "https://www.acmicpc.net/workbook"
        self.start_index = start
        self.end_index = end
        self.workbook_rank = 1
        self.proxy = config.PROXY_SERVER_IP
        logging.getLogger('scrapy.core.scraper').setLevel(logging.WARNING)

    def start_requests(self):
        for p_index in range(self.start_index, self.end_index + 1):
            url = f'{self.base_url}/top/{p_index}'
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={'proxy': self.proxy},
                errback=self.handle_error
            )

    def parse(self, response):
        if response.status != 200:
            self.logger.error(f"Failed to fetch {response.url}: HTTP {response.status}")
            return

        rows = response.css('.table.table-striped.table-bordered tr')[1:]

        for row in rows:
            cols = row.xpath('td').xpath('string(.)').getall()
            cols = [col.strip() for col in cols]
            workbook = defaultdict(lambda: None)
            workbook["workbook_rank"] = self.workbook_rank or None
            workbook["workbook_id"] = cols[0]
            workbook["user_id"] = cols[1]
            workbook["workbook_title"] = cols[2]
            workbook_id = workbook['workbook_id']
            problem_url = f'{self.base_url}/view/{workbook_id}'

            # self.logger.info(f"Requesting problem URL: {problem_url}")
            if workbook_id:
                yield scrapy.Request(url=problem_url,
                                     callback=self.parse_workbook_problems,
                                     meta={
                                         'proxy': self.proxy,
                                         'workbook': workbook
                                     },
                                     errback=self.handle_error
                                     )

            self.workbook_rank += 1

    def parse_workbook_problems(self, response):
        workbook = response.meta['workbook']
        # self.logger.info(f"Entered parse_workbook_problems with workbook: {workbook}")
        rows = response.css('.table.table-striped.table-bordered tr')[1:]
        for row in rows:
            cols = row.xpath('td').xpath('string(.)').getall()
            cols = [col.strip() for col in cols]

            workbook["problem_id"] = cols[0]
            workbook["problem_title"] = cols[1]

            item = WorkbookItem()
            item['workbook_rank'] = int(workbook["workbook_rank"])
            item['workbook_id'] = int(workbook["workbook_id"])
            item['user_id'] = workbook["user_id"]
            item['workbook_title'] = workbook["workbook_title"]
            item['problem_id'] = int(workbook["problem_id"])
            item['problem_title'] = workbook["problem_title"]

            # self.logger.info(f"Extracted Problem: {workbook}")
            yield item

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure}")

    def closed(self, reason):
        self.logger.info(f"Spider closed because {reason}")
