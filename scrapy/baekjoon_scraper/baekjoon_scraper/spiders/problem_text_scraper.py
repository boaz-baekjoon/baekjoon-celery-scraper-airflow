import logging
import scrapy
from baekjoon_scraper.items import ProblemTextItem
from baekjoon_scraper.config import config
from bs4 import BeautifulSoup
from w3lib.html import remove_tags
from typing import Optional
import time


class ProblemTextSpider(scrapy.Spider):
    name = 'problem_text_scraper'
    allowed_domains = ['acmicpc.net']
    proxy = config.PROXY_SERVER_IP
    start_urls = [f'https://www.acmicpc.net/problem/{i}' for i in range(1000, 30000)]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'HTTPERROR_ALLOWED_CODES': [301, 302, 400, 403, 404, 500]
    }

    def __init__(self, *args, **kwargs):
        super(ProblemSpider, self).__init__(*args, **kwargs)
        self.start_time = time.time()

    def start_requests(self):
        self.start_time = time.time()
        for index, url in enumerate(self.start_urls):
            yield scrapy.Request(url,
                                 callback=self.parse,
                                 meta={'proxy': self.proxy},
                                 )
            if (index + 1) % 500 == 0:
                time.sleep(3)

    def parse(self, response: scrapy.http.Response):
        if response.status != 200:
            self.logger.error(f"Failed to fetch {response.url}: HTTP {response.status}")
            return

        # Using XPath to find the problem title
        problem_title_xpath = "//div[@class='page-header']//*[@id='problem_title']/text()"
        # //div[@class='page-header']//*[@id="problem_title"]
        problem_name = response.xpath(problem_title_xpath).get()

        if problem_name is None:
            self.logger.error(f"Problem title not found in response from {response.url}")
            return

        problem_name: Optional[str] = problem_name.strip()
        # print("problem_name: ", problem_name)
        description_text: Optional[str] = self.fetch_paragraph(response, problem_name, "description")
        # print("description_text: ", description_text)
        input_text: Optional[str] = self.fetch_paragraph(response, problem_name, "input")
        # print("input_text : ", input_text)
        output_text: Optional[str] = self.fetch_paragraph(response, problem_name, "output")
        # print("output_text: ", output_text)

        item = ProblemTextItem()
        item['problem_id'] = int(response.url.split('/')[-1])
        item['problem_title'] = problem_name
        item['problem_text'] = description_text
        item['problem_input'] = input_text
        item['problem_output'] = output_text

        yield item

    def fetch_paragraph(self, response, problem_name, section_id):
        # Using XPath to extract text from the specified section

        paragraph_xpath = ""
        if section_id == "input":
            paragraph_xpath = f"//*[@id='problem_input']"
        elif section_id == "output":
            paragraph_xpath = f"//*[@id='problem_output']"
        else:
            paragraph_xpath = f"//*[@id='problem_description']"

        paragraphs = response.xpath(paragraph_xpath).getall()
        if len(paragraphs) == 0:
            self.logger.error(f"Problem : {problem_name} | Section {section_id} not found in response from {response.url}")
            return None

        return ' '.join([remove_tags(paragraph).strip() for paragraph in paragraphs])

    def closed(self, reason):
        end_time = time.time()  # Record end time
        total_time = end_time - self.start_time
        logging.info(f"Spider run time: {total_time:.2f} seconds")

    def handle_error(self, failure):
        # this will log the failure
        self.logger.error(repr(failure))