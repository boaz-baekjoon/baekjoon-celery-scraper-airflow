from celery_app.utils import create_celery
from crawler_process import run_spider, run_spiders_in_parallel
from custom_scraper.user_result_private_sequence import SubmitScraper_Concurrency
from celery import group
from multiprocessing import Process


celery_app = create_celery()

celery_app.conf.include = [
    "worker",
]


def run_spider_in_process(spider_name):
    def start_spider():
        # Function to start the spider
        run_spider(spider_name)

    process = Process(target=start_spider)
    process.start()
    process.join()

@celery_app.task
def start_spider_task(spider_name: str):
    if spider_name == 'user_result_pull_scraper':
        run_spiders_in_parallel(spider_name)
    else:
        run_spider_in_process(spider_name)


@celery_app.task
def start_crawl_user_private_sequence_task(user_name: str):
    ssc = SubmitScraper_Concurrency()
    result_df = ssc.gather(user_name)
