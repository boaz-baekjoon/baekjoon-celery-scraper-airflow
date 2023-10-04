import aiohttp
import asyncio
import random
import pandas as pd
import csv
import time
from bs4 import BeautifulSoup

csv_file_path = "./bj_users.csv"


class UserScraper:
    def __init__(self):
        self.agents_list = [
            "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        ]
        self.semaphore = asyncio.Semaphore(10)

        self.results_df = pd.DataFrame(
            columns=["user_id", "맞은 문제", "맞았지만 만점을 받지 못한 문제", "시도했지만 맞지 못한 문제"]
        )  # 결과를 저장할 pandas DataFrame 초기화

    async def get_problem_numbers(self, session, user_id, user_url):
        try:
            headers = {"User-Agent": random.choice(self.agents_list)}
            async with session.get(user_url, headers=headers, ssl=False) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    problem_table = soup.find_all("div", {"class": "panel panel-default"})
                    ac, wa, tle = [], [], []

                    interested_title = {"맞은 문제": ac, "맞았지만 만점을 받지 못한 문제": wa, "시도했지만 맞지 못한 문제": tle}

                    for each_table in problem_table:
                        table_title = each_table.find("h3").text
                        if table_title not in interested_title.keys():
                            continue

                        et = each_table.find("div", {"class": "problem-list"})
                        result = [a.text for a in et.find_all("a")]
                        interested_title[table_title].extend(result)

                    return ac, wa, tle

                else:
                    print(f"Error - Status Code {response.status} for user ID: {user_id}")
                    return None, None, None
        except Exception as e:
            print("Error occurred: ", e)
            return [], [], []

    async def fetch_user_data(self, session, user_id):
        user_page_url = f"https://www.acmicpc.net/user/{user_id}"

        await asyncio.sleep(5.0)

        async with self.semaphore:
            ac, wa, tle = await self.get_problem_numbers(session, user_id, user_page_url)
        return user_id, ac, wa, tle

    def save_to_csv(self, user_id, ac, wa, tle):
        self.results_df = pd.concat(
            [
                self.results_df,
                pd.DataFrame(
                    {  # 결과를 DataFrame에 추가
                        "user_id": [user_id],
                        "맞은 문제": [ac if ac else "None"],
                        "맞았지만 만점을 받지 못한 문제": [wa if wa else "None"],
                        "시도했지만 맞지 못한 문제": [tle if tle else "None"],
                    }
                ),
            ],
            ignore_index=True,
        )

    def save_results_to_csv(self, filename):  # DataFrame을 CSV 파일로 저장
        self.results_df.to_csv(filename, index=False, encoding="utf-8")


async def main():
    scraper = UserScraper()

    async with aiohttp.ClientSession() as session:
        with open(csv_file_path, "r", newline="", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)

            tasks = []
            for idx, row in enumerate(csv_reader, start=1):
                if idx >= 1 and idx <= 120000:
                    user_id = row["user_id"]
                    task = scraper.fetch_user_data(session, user_id)
                    tasks.append(task)
                elif idx > 120000:
                    break

            results = await asyncio.gather(*tasks)

            for user_id, ac, wa, tle in results:
                if ac or wa or tle:
                    scraper.save_to_csv(user_id, ac, wa, tle)
                    print(f"{user_id}_problem_results.csv'로 저장되었습니다.")
                else:
                    print(f"{user_id}에 대한 크롤링 실패")

    scraper.save_results_to_csv("users_result.csv")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    start = time.time()
    result = loop.run_until_complete(main())
    end = time.time()
    print(f"실행 시간 = {end - start}s")
    loop.close()
