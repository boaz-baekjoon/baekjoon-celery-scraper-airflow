from fastapi import FastAPI, HTTPException, Depends
from starlette.responses import JSONResponse
from async_problem_text import ProblemScraper
import aiohttp
import asyncio
import os
import logging

app = FastAPI()

async def get_scraper() -> ProblemScraper:
    base_url = "https://www.acmicpc.net/problem/"
    scraper = ProblemScraper(base_url)
    return scraper

async def get_aiohttp_session() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()

async def main_routine(scraper: ProblemScraper, session: aiohttp.ClientSession):
    for i in range(1, 28499, 500):
        tasks = [scraper.fetch_problem_text(p_index, session) for p_index in range(i, i + 500)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(3)

@app.get("/scrape-text/")
async def scrape_problems(
    scraper: ProblemScraper = Depends(get_scraper),
    session: aiohttp.ClientSession = Depends(get_aiohttp_session)
):
    try:
        await main_routine(scraper, session)

        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(output_folder, exist_ok=True)

        file_path = os.path.join(output_folder, "problems_text.csv")
        scraper.save_to_csv(file_path)
        
        return JSONResponse(content={"message": "Scraping completed!", "file_path": file_path}, status_code=200)
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail="Scraping failed.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)