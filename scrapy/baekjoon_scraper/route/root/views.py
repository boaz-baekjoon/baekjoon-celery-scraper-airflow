from fastapi import APIRouter, HTTPException, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

from worker import (
    celery_app,
)
from typing import Dict


root_router = APIRouter()


@root_router.get("/", response_class=JSONResponse, status_code=200)
async def read_root() -> Dict[str, str]:
    '''
    api health check를 위한 API
    '''
    return {"response": "Hello World"}


@root_router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if not task_result.ready():
        return {"status": "pending"}
    return {
        "status": "completed",
        "result": task_result.result
    }