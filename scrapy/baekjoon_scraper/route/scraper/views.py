from fastapi import APIRouter, HTTPException, Query
from starlette.responses import JSONResponse
import logging
from typing import Dict

from route.scraper.database import get_user_info
from connection.redis import redis_client
from worker import (
    celery_app,
    start_spider_task,
    start_crawl_user_private_sequence_task, start_crawl_user_private_sequence_task_all
)

crawler_router = APIRouter()


@crawler_router.post("/start-scrapy-spider/")
async def start_crawler(spider_name: str):
    '''
    크롤러를 시작하는 API \n
    spider_name: 크롤러 이름 \n
    baekjoon_problem \n
    baekjoon_problem_detail \n
    baekjoon_user \n
    beakjoon_user_detail \n
    problem_text_scraper \n
    user_result_pull_scraper \n
    workbook_scraper \n

    Parameters
    ----------
    spider_name

    Returns
    -------
    '''
    if not spider_name:
        return {"error": "Spider name is required"}

    if spider_name == 'user_result_push_scraper':
        result = start_spider_task.apply(args=[spider_name])
        return {
            "message": f"finished crawling {spider_name}",
            "task_result": result.get()
        }
    else:
        task = start_spider_task.delay(spider_name)
        return {"message": f"Started crawling {spider_name}", "task_id": task.id}


@crawler_router.post("/crawl-user-private-sequence/")
async def crawl_sequence_crawler(user_id: str):
    '''
    유저 문제 크롤러를 시작하는 API \n
    Parameters
    ----------
    user_id

    Returns
    -------

    '''
    if not user_id:
        return {"error": "user_id is required"}

    task = start_crawl_user_private_sequence_task.delay(user_id)
    return {
        "message": f"Started private sequence crawling {user_id}",
        "task_id": task.id
    }


@crawler_router.post("/crawl-user-private-sequence-sync/")
async def crawl_sync_sequence_crawler(user_id: str):
    if not user_id:
        return {"error": "user_id is required"}

    task = start_crawl_user_private_sequence_task.delay(user_id)
    result = task.get(timeout=60)  # 60초 동안 태스크의 결과를 기다림
    return {
        "message": f"Completed private sequence crawling {user_id}",
        "result": result
    }


@crawler_router.post("/crawl-user-result-push")
async def crawl_user_result_push():
    user_info = get_user_info()
    if not user_info:
        raise HTTPException(status_code=500, detail="Failed to fetch user info")

    await redis_client.delete('user_result_page_url')

    for user in user_info:
        if user['user_rank'] <= 120000:
            user_page_url = f"https://www.acmicpc.net/user/{user['user_id']}"
            await redis_client.lpush('user_result_page_url', user_page_url)

    return {"message": "Saved user result page url to redis"}


@crawler_router.post("/crawl-user-private-sequence-all/")
async def crawl_sync_sequence_crawler():
    task = start_crawl_user_private_sequence_task_all.delay()
    return {
        "message": f"Started total private sequence crawling",
        "task_id": task.id
    }
