from airflow import DAG
from airflow.operators.empty import EmptyOperator

from airflow.utils.dates import days_ago
from custom_http_plugin.long_http_operator import CustomSimpleHttpOperator
import logging

dag_configs = [
    {
        "dag_id": "baekjun_problem_dag",
        "description": "baekjun_problem_dag by operator",
        "tags": ["http", "baekjun_problem_dag"],
        "schedule_interval": "0 4 * * 3",
        "spider_name": "baekjoon_problem",
    },
    {
        "dag_id": "baekjoon_user_dag",
        "description": "baekjoon_user_dag by operator",
        "tags": ["http", "baekjoon_user_dag"],
        "schedule_interval": "0 5 * * 3",
        "spider_name": "baekjoon_user",
    },
    {
        "dag_id": "workbook_scraper_dag",
        "description": "workbook_scraper by operator",
        "tags": ["http", "workbook_scraper_dag"],
        "schedule_interval": "0 6 * * 3",
        "spider_name": "workbook_scraper",
    },
    {
        "dag_id": "baekjoon_problem_detail_dag",
        "description": "baekjoon_problem_detail_dag by operator",
        "tags": ["http", "baekjoon_problem_detail_dag"],
        "schedule_interval": "0 7 * * 3",
        "spider_name": "baekjoon_problem_detail",
    },
    {
        "dag_id": "beakjoon_user_detail_dag",
        "description": "beakjoon_user_detail_dag by operator",
        "tags": ["http", "beakjoon_user_detail_dag"],
        "schedule_interval": "0 9 * * 2",
        "spider_name": "beakjoon_user_detail",
    },
    {
        "dag_id": "problem_text_scraper_dag",
        "description": "problem_text_scraper_dag by operator",
        "tags": ["http", "problem_text_scraper_dag"],
        "schedule_interval": "0 11 * * 3",
        "spider_name": "problem_text_scraper",
    },
]

default_args = {
    "owner": "yoohajun",
    "depends_on_past": False,
    "catchup": False,
}


def handle_response(response):
    """Handle API response."""
    logging.info(response.text)
    if response.status_code == 200:
        logging.info(response.json())
    else:
        logging.error(response.text)
        raise ValueError("API call failed: " + response.text)


for config in dag_configs:
    with DAG(
            dag_id=config["dag_id"],
            description=config["description"],
            tags=config["tags"],
            schedule_interval=config["schedule_interval"],
            start_date=days_ago(1),
            default_args=default_args,
    ) as dag:
        start_sensor = EmptyOperator(task_id="start")
        end_sensor = EmptyOperator(task_id="end")

        HTTP_CONN_ID = 'baekjun_scraper_api'
        SPIDER_NAME = config["spider_name"]

        crawler_task = CustomSimpleHttpOperator(
            task_id=f"call_crawler",
            http_conn_id=HTTP_CONN_ID,
            endpoint=f"/v1/crawl/start-scrapy-spider/?spider_name={SPIDER_NAME}",
            method="POST",
            headers={"Content-Type": "application/json"},
            response_check=lambda response: handle_response(response),
        )

        start_sensor >> crawler_task >> end_sensor

    globals()[config["dag_id"]] = dag
