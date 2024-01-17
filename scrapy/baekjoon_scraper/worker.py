from celery_app.utils import create_celery
from crawler_process import run_spider
from route.scraper.service import SubmitScraper_Concurrency
from route.scraper.database import get_user_id
from celery import group, chain
import logging
from typing import List

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


@celery_app.task
def start_crawl_user_private_sequence_task(user_id: str):
    ssc = SubmitScraper_Concurrency()
    result_flag = ssc.gather(user_id)
    return result_flag


@celery_app.task
def scrape_and_update_user(user: dict) -> bool:
    ssc = SubmitScraper_Concurrency()
    result_flag = ssc.gather(user["user_id"])
    if result_flag:
        logging.info(f"Successfully crawled {user['user_id']}")
    else:
        logging.error(f"Failed to crawl {user['user_id']}")
    return result_flag


def split_into_sublists(lst: List, n: int) -> List[List]:
    """Splits a list into n roughly equal sublists."""
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


@celery_app.task
def start_crawl_user_private_sequence_task_all():
    user_info = get_user_id()
    logging.info(f"Total number of users: {len(user_info)}")

    # Split user_info into 4 sub-lists
    sub_lists = split_into_sublists(user_info, 4)

    # Create a group of sub-tasks
    crawl_tasks = group(
        scrape_and_update_user.s(user)
        for sublist in sub_lists
        for user in sublist
        if user['user_rank'] <= 120000
    )

    # Chain the group with a callback task
    job = chain(crawl_tasks, process_crawl_results.s())
    
    # Execute the chain of tasks without waiting for the result
    job.apply_async()


@celery_app.task
def process_crawl_results(result_list):
    # Process the results here
    update_cnt = sum(result_list)
    return update_cnt