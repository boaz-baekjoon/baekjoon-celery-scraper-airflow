from abc import ABC, abstractmethod
import scrapy

class BaseSpider(scrapy.Spider, ABC):

    @abstractmethod
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def start_requests(self):
        pass

    @abstractmethod
    def parse(self, response: scrapy.http.Response):
        pass

    @abstractmethod
    def closed(self, reason):
        pass

    @abstractmethod
    def handle_error(self, failure):
        pass
