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
        dag_id="user_sequence_all_crawler_dag",
        description="all user_sequence_crawler_dag by operator",
        tags=["http", "all", "user_sequence_crawler_dag"],
        schedule_interval="0 5 * * 1",
        start_date=days_ago(1),
        default_args=default_args,
) as dag:
    start_sensor = EmptyOperator(task_id="start")
    end_sensor = EmptyOperator(task_id="end")

    HTTP_CONN_ID = 'baekjun_scraper_api'

    crawler_task = CustomSimpleHttpOperator(
        task_id=f"call_crawler_user_sequence_api",
        http_conn_id=HTTP_CONN_ID,
        endpoint=f"/v1/crawl/crawl-user-private-sequence-all",
        method="POST",
        headers={"Content-Type": "application/json"},
        response_check=lambda response: handle_response(response),
    )

    start_sensor >> crawler_task >> end_sensor

