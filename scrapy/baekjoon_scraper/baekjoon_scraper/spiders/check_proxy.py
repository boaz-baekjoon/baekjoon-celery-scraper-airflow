import scrapy
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from baekjoon_scraper.config import config

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

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.driver = None

    def get_proxy(self):
        return random.choice(self.proxies)

    def start_requests(self):
        logger.info("start crawl")
        url = "https://www.whatismyip.com"

        # Initialize Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        # Set proxy for Chrome
        proxy_argument = f'--proxy-server={self.get_proxy()}'
        options.add_argument(proxy_argument)

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                       options=options)

        yield scrapy.Request(url, self.parse, meta={'proxy': self.get_proxy()})

    def parse(self, response):
        # Use Selenium to get the page
        self.driver.get(response.url)

        # Wait for the specific element to be loaded
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'tool-what-is-my-ip'))
            )

            # Now extract the IP information
            ip_info_element = self.driver.find_element(By.ID, 'tool-what-is-my-ip')
            ip_info = ip_info_element.text.strip() if ip_info_element else 'Not found'
        except Exception as e:
            ip_info = f'Error occurred: {str(e)}'

        # Log IP information
        logger.info(f"IP Information: {ip_info}")

        # Close the browser
        self.driver.quit()