import scrapy
import json
from baekjoon_scraper.items import UserDetailItem
from baekjoon_scraper.config import config
from scrapy.utils.response import response_status_message
import time
import logging


class UserDetailSpider(scrapy.Spider):
    name = 'beakjoon_user_detail'
    allowed_domains = ['solved.ac']
    start_urls = ['https://solved.ac/api/v3/ranking/tier']

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_DELAY': 3,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429]
    }

    def __init__(self, *args, **kwargs):
        super(UserDetailSpider, self).__init__(*args, **kwargs)
        self.start_time = time.time()

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,
                                 callback=self.parse,
                                 # meta={'proxy': self.get_proxy()}
                                 )

    def parse(self, response):
        data = json.loads(response.text)
        count = data['count']
        max_page = count // 50 + 1
        for page in range(1, max_page + 1):
            next_page = f"https://solved.ac/api/v3/ranking/tier?page={page}"
            yield scrapy.Request(next_page,
                                 callback=self.parse_page,
                                 # meta={'proxy': self.get_proxy()}
                                 )

    def parse_page(self, response):
        if response.status != 200:
            # Handle non-200 responses
            reason = response_status_message(response.status)
            self.retry_request(response, reason)
            return

        data = json.loads(response.text)
        items = data['items']
        for item in items:
            if item['tier'] == 5:
                break

            yield UserDetailItem(
                user_id=item['handle'],
                user_answer_num=item['solvedCount'],
                user_tier=item['tier'],
                user_rating=item['rating'],
                user_rating_by_problems_sum=item['ratingByProblemsSum'],
                user_rating_by_class=item['ratingByClass'],
                user_rating_by_solved_count=item['ratingBySolvedCount'],
                user_rating_by_vote_count=item['ratingByVoteCount'],
                user_class=item['class'],
                user_max_streak=item['maxStreak'],
                user_joined_at=item['joinedAt'],
                user_rank=item['rank'],
            )
            # logging.info(f"User {item['handle']} crawled")

    def retry_request(self, response, reason):
        retry_times = response.meta.get('retry_times', 0) + 1
        if retry_times <= self.custom_settings['RETRY_TIMES']:
            logging.warning(f"Retrying {response.url} due to {reason} (retry {retry_times})")
            retryreq = response.request.copy()
            retryreq.meta['retry_times'] = retry_times
            yield retryreq
        else:
            logging.error(f"Gave up retrying {response.url} after {retry_times} retries")

    @staticmethod
    def get_proxy():
        proxy_ip = config.PROXY_SERVER_IP
        return proxy_ip

    def closed(self, reason):
        end_time = time.time()  # Record end time
        total_time = end_time - self.start_time
        logging.info(f"Spider run time: {total_time:.2f} seconds")
