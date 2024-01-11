from fastapi import FastAPI, HTTPException, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
import logging
from typing import Dict

from route.scraper.views import crawler_router
from worker import (
    celery_app,
    start_spider_task,
    start_crawl_user_private_sequence_task
)

import time
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 로그 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    request_log = {
        "type": "request",
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
    }
    logger.info(json.dumps(request_log))

    response: Response = await call_next(request)

    response_log = {
        "type": "response",
        "status_code": response.status_code,
        "headers": dict(response.headers),
    }
    logger.info(json.dumps(response_log))

    process_time = time.time() - start_time
    logger.info(json.dumps({"type": "performance", "duration": f"{process_time:.2f}"}))

    return response


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


app.include_router(crawler_router, prefix="/v1/crawl", tags=["crawler"])