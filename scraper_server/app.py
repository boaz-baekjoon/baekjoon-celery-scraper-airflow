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

@app.get("/scrape-text/")
async def scrape_problems():
    try:
        base_url = "https://www.acmicpc.net/problem/"
        scraper = ProblemScraper(base_url)

        async def main_routine():
            async with aiohttp.ClientSession() as session:
                for i in range(1, 28499, 500):
                    logger.info(f"Scraping problems from index {i} to {i + 499}...")
                    tasks = [scraper.fetch_problem_text(p_index, session) for p_index in range(i, i + 500)]
                    await asyncio.gather(*tasks)
                    await asyncio.sleep(3)

        await main_routine()

        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(output_folder, exist_ok=True)

        file_path = os.path.join(output_folder, "problems_text.csv")
        scraper.save_to_csv(file_path)
        logger.info(f"Data saved to {file_path}")

        return JSONResponse(content={"message": "Scraping completed!", "file_path": file_path}, status_code=200)

    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail="Scraping failed.")


