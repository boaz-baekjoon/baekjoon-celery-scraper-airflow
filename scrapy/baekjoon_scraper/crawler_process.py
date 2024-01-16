from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from baekjoon_scraper.spiders.baekjoon_user import BaekjoonUserSpider
from baekjoon_scraper.spiders.baekjoon_problem_detail import ProblemDetailSpider
from baekjoon_scraper.spiders.baekjoon_problem import ProblemsetSpider
from baekjoon_scraper.spiders.baekjoon_user_detail import UserDetailSpider
from baekjoon_scraper.spiders.problem_text_scraper import ProblemTextSpider
from baekjoon_scraper.spiders.workbook_scraper import WorkbookScraperSpider
from baekjoon_scraper.spiders.user_result_pull_scraper import UserResultPullScraperSpider
from baekjoon_scraper.spiders.user_result_push_scraper import UserResultPushScraperSpider
import logging
from threading import Thread
import subprocess


class SpiderFactory:
    @staticmethod
    def get_spider(spider_name):
        spiders = {
            'baekjoon_user': BaekjoonUserSpider,
            'baekjoon_problem_detail': ProblemDetailSpider,
            'baekjoon_problem': ProblemsetSpider,
            'beakjoon_user_detail': UserDetailSpider,
            'problem_text_scraper': ProblemTextSpider,
            'workbook_scraper': WorkbookScraperSpider,
            'user_result_push_scraper': UserResultPushScraperSpider,
            'user_result_pull_scraper': UserResultPullScraperSpider
        }
        return spiders.get(spider_name, None)


# def run_spider(spider_name):
#     spider = SpiderFactory.get_spider(spider_name)
#     if spider is None:
#         logging.error(f"Spider not found: {spider_name}")
#         return
#
#     process = CrawlerProcess(get_project_settings())
#     process.crawl(spider)
#     process.start()

def run_spider(spider_name: str):
    try:
        command = ["scrapy", "crawl", spider_name]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running spider: {e}")


def run_spiders_in_parallel(spider_name, number_of_threads=10):
    threads = []
    for _ in range(number_of_threads):
        thread = Thread(target=run_spider, args=(spider_name,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    import sys

    spider_name = sys.argv[1]
    if not spider_name:
        print("Please specify spider name")
        sys.exit(1)

    if spider_name == 'user_result_pull_scraper':
        run_spiders_in_parallel(spider_name)
    else:
        run_spider(spider_name)
