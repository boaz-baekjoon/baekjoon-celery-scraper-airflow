from fastapi import FastAPI, HTTPException, Depends
from starlette.responses import JSONResponse
import logging
from typing import Dict
from worker import (
    celery_app,
    start_spider_task,
    start_crawl_user_private_sequence_task
)

app = FastAPI()

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/", response_class=JSONResponse, status_code=200)
async def read_root() -> Dict[str, str]:
    '''
    api health check를 위한 API
    '''
    return {"response": "Hello World"}



@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if not task_result.ready():
        return {"status": "pending"}
    return {
        "status": "completed",
        "result": task_result.result
    }

# @app.post("/crawl-user-private-sequence/")
# async def crawl_crawler(user_id: str):
#     if not user_id:
#         return {"error": "user_id is required"}
#
#     task = start_crawl_user_private_sequence_task.delay(user_id)
#     result = task.get(timeout=30)  # 30초 동안 태스크의 결과를 기다림
#     return {
#         "message": f"Completed private sequence crawling {user_id}",
#         "result": result
#     }