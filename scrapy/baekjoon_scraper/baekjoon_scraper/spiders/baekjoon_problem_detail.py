import scrapy
import json

from baekjoon_scraper.config import config

from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
from baekjoon_scraper.items import ProblemDetailItem


class ProblemDetailSpider(scrapy.Spider):
    name = 'baekjoon_problem_detail'
    allowed_domains = ['solved.ac']
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 0,
        'RANDOMIZE_DOWNLOAD_DELAY': False
    }

    def start_requests(self):
        url = 'https://solved.ac/api/v3/problem/lookup/?problemIds='
        problem_ids = self._get_problem_id()
        bet_url = '%2C'
        for i in range(len(problem_ids) // 100 + 1):
            start = i * 100
            end = min((i + 1) * 100, len(problem_ids))
            # Convert integer IDs to strings
            param = bet_url.join(map(str, problem_ids[start:end]))
            final_url = url + param
            yield scrapy.Request(final_url,
                                 callback=self.parse,
                                 # meta={'proxy': self.get_proxy()},
                                 )

    def parse(self, response):
        data = json.loads(response.text)
        for item in data:
            transformed_data = self._transform(item)
            for transformed_item in transformed_data:
                # self.logger.info(transformed_item)
                yield transformed_item

    def _get_problem_id(self):
        # problem_ids 가져오기의 로직 구현
        engine = self.init_db()
        Session = sessionmaker(bind=engine)
        session = Session()

        metadata = MetaData()
        problems_table = Table('problems', metadata, autoload_with=engine)

        # problems 테이블에서 problem_id 가져오기
        query = session.query(problems_table.c.problem_id)
        problem_ids = [row.problem_id for row in query.all()]
        problem_ids = list(set(problem_ids))
        session.close()

        return problem_ids

    @staticmethod
    def init_db():
        username = config.DB_USER
        password = config.DB_PASSWORD
        host = config.DB_HOST
        port = config.DB_PORT
        database = config.DB_NAME
        engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

        return engine

    @staticmethod
    def _transform(item):
        transformed_data = []
        title_info = item.get('titles', [{}])[0]
        tags = item.get('tags', [])

        for tag in tags:
            transformed_item = ProblemDetailItem(
                problem_id=item.get('problemId'),
                problem_title=item.get('titleKo'),
                problem_lang=title_info.get('language'),
                tag_display_lang=title_info.get('languageDisplayName'),
                tag_name=title_info.get('title'),
                problem_titles_is_original=title_info.get('isOriginal'),
                problem_is_solvable=item.get('isSolvable'),
                problem_is_partial=item.get('isPartial'),
                problem_answer_num=item.get('acceptedUserCount'),
                problem_level=item.get('level'),
                problem_voted_user_count=item.get('votedUserCount'),
                problem_sprout=item.get('sprout'),
                problem_gives_no_rating=item.get('givesNoRating'),
                problem_is_level_locked=item.get('isLevelLocked'),
                problem_average_tries=item.get('averageTries'),
                problem_official=item.get('official'),
                tag_key=tag['key']
            )
            transformed_data.append(transformed_item)

        return transformed_data

    @staticmethod
    def get_proxy():
        proxy_ip = config.PROXY_SERVER_IP
        return proxy_ip
