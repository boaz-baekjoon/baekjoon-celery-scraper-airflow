from fastapi import FastAPI, HTTPException, Depends
from starlette.responses import JSONResponse
from async_problem_text import ProblemScraper
import aiohttp
import asyncio
import os
import logging
from typing import Dict

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

