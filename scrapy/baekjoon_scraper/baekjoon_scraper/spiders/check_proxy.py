import scrapy
from baekjoon_scraper.spiders.base_spider import BaseSpider
from baekjoon_scraper.config import config
from scrapy_splash import SplashRequest

import logging
import random

logger = logging.getLogger('check_proxy')
logger.setLevel(logging.DEBUG)

class CheckProxySpider(scrapy.Spider):
    name = "check_proxy"
    allowed_domains = ["www.whatismyip.com"]
    proxies = [
        config.PROXY_SERVER_IP
    ]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False
    }

    def start_requests(self):
        logger.info("start crawl")
        url = "https://www.whatismyip.com"
        proxy = random.choice(self.proxies)
        yield SplashRequest(
            url=url,
            callback=self.parse,
            meta={'proxy': proxy},
            args={'wait': 2}
        )

    def parse(self, response):
        # IP 정보 추출
        ip_info = response.xpath('//*[@id="tool-what-is-my-ip"]').getall()
        ip_info = [i.strip() for i in ip_info if i.strip()]

        # 로그로 IP 정보 출력
        logger.info(f"IP Information: {ip_info}")
