from celery_app.utils import create_celery
from crawler_process import run_spider
from custom_scraper.user_result_private_sequence import SubmitScraper_Concurrency
from celery import group
from multiprocessing import Process


celery_app = create_celery()

celery_app.conf.include = [
    "worker",
]


def run_spiders_in_parallel(spider_name, number_of_spiders=4):
    return group([spider_task.s(spider_name) for _ in range(number_of_spiders)])()

def run_user_result_scrapers_in_sequence():
    return chain(user_result_push_scraper_task.s(), user_result_pull_scraper_task.s())()

@celery_app.task
def spider_task(spider_name: str):
    run_spider(spider_name)

@celery_app.task
def start_spider_task(spider_name: str):
    if spider_name == 'user_result_pull_scraper':
        return run_spiders_in_parallel(spider_name)
    elif spider_name == "user_result":
        return run_user_result_scrapers_in_sequence()
    else:
        return spider_task.delay(spider_name)

@celery_app.task
def user_result_push_scraper_task():
    return spider_task.delay(spider_name="user_result_push_scraper")

@celery_app.task
def user_result_pull_scraper_task():
    return run_spiders_in_parallel(spider_name="user_result_pull_scraper")