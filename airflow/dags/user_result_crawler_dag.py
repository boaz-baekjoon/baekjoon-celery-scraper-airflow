from airflow import DAG
from airflow.operators.empty import EmptyOperator

from airflow.utils.dates import days_ago
from custom_http_plugin.long_http_operator import CustomSimpleHttpOperator
import logging

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


with DAG(
        dag_id="user_result_crawler_dag",
        description="user_result_crawler_dag by operator",
        tags=["http", "user_result_crawler_dag"],
        schedule_interval="0 3 * * 4",
        start_date=days_ago(1),
        default_args=default_args,
) as dag:
    start_sensor = EmptyOperator(task_id="start")
    end_sensor = EmptyOperator(task_id="end")

    HTTP_CONN_ID = 'baekjun_scraper_api'
    spider_list = ['user_result_push_scraper', 'user_result_pull_scraper']
    end_points = [
        "/v1/crawl/crawl-user-result-push",
        "/v1/crawl/start-scrapy-spider/?spider_name=user_result_pull_scraper"
    ]

    last_task = start_sensor
    for spider_name, end_point in zip(spider_list, end_points):
        crawler_task = CustomSimpleHttpOperator(
            task_id=f"call_crawler_{spider_name}",
            http_conn_id=HTTP_CONN_ID,
            endpoint=end_point,
            method="POST",
            headers={"Content-Type": "application/json"},
            response_check=lambda response: handle_response(response),
        )
        last_task >> crawler_task
        last_task = crawler_task

    last_task >> end_sensor

