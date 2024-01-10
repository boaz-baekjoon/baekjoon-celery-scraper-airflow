import os
import random
from typing import List, Dict, Any

import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import asyncio
import time
import logging


class ProblemScraper:
    def __init__(self, url: str):
        self.base_url = url
        self.problems: List[Dict[str, Any]] = []

    async def fetch_problem_text(self, p_index: int, session: aiohttp.ClientSession):
        url = f"{self.base_url}{p_index}"
        # print(f"Fetching data for problem index {p_index} from {url}")
        
        user_agents_list = [
            'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        ]

        headers = {'User-Agent': random.choice(user_agents_list)}
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    header_field = soup.find(class_='page-header')
                    problem_name: str = header_field.find("span", id="problem_title").text.strip()

                    description_text = self.fetch_paragraph(soup, "description", "problem-text")
                    input_text = self.fetch_paragraph(soup, "input", "problem-text")
                    output_text = self.fetch_paragraph(soup, "output", "problem-text")

                    problem = {
                        "id": p_index,
                        "problem_title": problem_name,
                        "problem_text": description_text,
                        "problem_input": input_text,
                        "problem_output": output_text
                    }

                    self.problems.append(problem)
                    # print(f"Success Fetching data for problem index {p_index} from {url}")
                    return  # If everything went fine, just return from the function
                

        except (aiohttp.ClientError, ValueError) as e:  # catch expected exceptions
            logging.error(f"Error fetching data for problem index {p_index}. Error: {e}")
            await asyncio.sleep(2)  # Give it a bit more sleep before retrying, just in case

        except Exception as e:  # Catch unexpected exceptions
            logging.error(f"Unexpected error for problem index {p_index}. Error: {e}")
            pass


    @staticmethod
    def fetch_paragraph(soup: BeautifulSoup, section_id: str, find_class: str) -> str:
        problem_description = soup.find("section", id=section_id)
        text_fields = problem_description.find(class_=find_class)
        paragraphs: List[str] = [row.text.strip() for row in text_fields.find_all('p')]
        return ' '.join(paragraphs)

    def save_to_csv(self, file_name: str):
        df = pd.DataFrame(self.problems)
        df.sort_values(by=['id'], inplace=True)
        df.to_csv(file_name, index=False, encoding='utf-8-sig')


if __name__ == "__main__":
    base_url = "https://www.acmicpc.net/problem/"
    scraper = ProblemScraper(base_url)

    async def main_routine():
        async with aiohttp.ClientSession() as session:
            for i in range(1, 28499, 500):
                tasks = [scraper.fetch_problem_text(p_index, session) for p_index in range(i, i + 500)]
                await asyncio.gather(*tasks)
                await asyncio.sleep(3)

    asyncio.run(main_routine())

    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_folder, exist_ok=True)

    file_path = os.path.join(output_folder, "problems_text.csv")
    scraper.save_to_csv(file_path)
    print(file_path)