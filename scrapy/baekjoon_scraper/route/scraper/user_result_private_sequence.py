import random
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import pandas as pd
from route.scraper.database import upsert_user_sequence
import logging

class SubmitScraper_Concurrency:
    def __init__(self):
        self.agents_list = [
            'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        ]
        self.user_id = None

    def gather(self, user_id: str) -> bool:
        submits_from_tasks = list()
        self.user_id = user_id

        tables = self.gather_table_documents()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = {executor.submit(self.gather_table_rows, tab): (i, tab) for i, tab in enumerate(tables)}

            for future in concurrent.futures.as_completed(tasks):
                valid_order = tasks[future][0]

                try:
                    result = future.result()
                    submits_from_tasks.append([valid_order, result])
                except Exception as e:
                    print(f'{valid_order} 번째 태스크에서 예외 발생: ', e)

        submits_from_tasks.sort(key=lambda task: task[0])

        submits = list()
        sentinel = (0, '0')
        submits.append(sentinel)

        for submits_block in submits_from_tasks:
            for submit in submits_block[1]:
                # if submit != submits[-1][1]:
                index = len(submits)
                submits.append((index, submit))

        del submits[0]

        df = pd.DataFrame(submits, columns=['user_id', 'problem'])

        df['user_id'] = user_id
        result_tuple_str = str(tuple(df['problem']))

        result_flag: bool = upsert_user_sequence(
            user_id=user_id,
            problem_sequence=result_tuple_str
        )

        logging.warning(f"result_flag: {result_flag}, user_id: {user_id}")

        return result_flag

    def gather_table_documents(self) -> list:
        documents = list()

        document = self.fetch_document(self.user_id)

        while True:
            tag_top = document.find('a', {'id': 'next_page'})

            documents.append(document)

            if not tag_top:
                break

            next_top = tag_top['href'].split("&")[1]

            document = self.fetch_document(self.user_id, next_top)

        return documents

    def fetch_document(self, user_id: str, top: str = None):
        link = "https://www.acmicpc.net/status?" + "user_id=" + user_id + ("" if not top else "&" + top)

        document = BeautifulSoup(requests.get(link, headers={'User-Agent': random.choice(self.agents_list)}).text,
                                 "html.parser")

        return document

    def gather_table_rows(self, table):
        submits = list()

        for row in table.find('tbody').find_all('tr'):
            problem = row.find_all('td')[2].text
            result = row.find('td', class_='result').find('span').text

            result = result.replace('\xa0', ' ')

            submits.append(problem)

        return submits

