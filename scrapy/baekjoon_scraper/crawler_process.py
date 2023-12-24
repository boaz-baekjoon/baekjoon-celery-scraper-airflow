from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from baekjoon_scraper.spiders.baekjoon_user import BaekjoonUserSpider
from baekjoon_scraper.spiders.baekjoon_problem_detail import ProblemDetailSpider
from baekjoon_scraper.spiders.baekjoon_problem import ProblemsetSpider
from baekjoon_scraper.spiders.baekjoon_user_detail import UserDetailSpider
from baekjoon_scraper.spiders.problem_text_scraper import ProblemTextSpider
from baekjoon_scraper.spiders.workbook_scraper import WorkbookScraperSpider
from baekjoon_scraper.spiders.user_result_scraper import UserResultScraperSpider


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
            'user_result_scraper': UserResultScraperSpider
        }
        return spiders.get(spider_name, None)


def run_spider(spider_name):
    spider = SpiderFactory.get_spider(spider_name)
    if spider is None:
        print(f"Spider not found: {spider_name}")
        return

    process = CrawlerProcess(get_project_settings())
    process.crawl(spider)
    process.start()


if __name__ == "__main__":
    import sys

    spider_name = sys.argv[1]
    if spider_name is None:
        print("Please specify spider name")
        sys.exit(1)

    run_spider(spider_name)
