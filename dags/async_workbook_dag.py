from airflow import DAG

from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from datetime import datetime, timedelta

from plugins import async_crawler
from airflow.decorators import task # decorator 임포트

import asyncio
import os

import logging
import time


@task
def scrape_workbook_user(url:str, start:int, end:int, flag:str) -> list:
    base_url = url
    start = start
    end = end
    print('start scrape_workbook_user task')
    start_time = time.time()
    
    scraper = async_crawler.Scraper(flag=flag)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scraper.get_object_thread(base_url = base_url, start = start, end = end))
    loop.close()     
    
    end_time = time.time()
    print(f'scrape_workbook_user {start_time-end_time} seconds')
    return scraper.workbooks


@task
def save_to_csv(scraper_object:list, flag:str) -> None:
    
    print('start save_to_csv task')
    scraper = async_crawler.Scraper(flag=flag)
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    file_path = os.path.join(output_folder, f"workbooks.csv")
    scraper.save_to_csv(objects=scraper_object, file_name=file_path)
    print('end save_to_csv task')
    

@task
def upload_local_file_to_s3(csv_file:str, s3_key:str, s3_bucket_name:str, s3_hook) -> None:
    logging.info("Start upload!")
    
    logging.info(f'{s3_key}' + " upload to " + f'{s3_bucket_name}')
    
    s3_hook.load_file(
        filename=csv_file,
        key= s3_key,
        bucket_name=s3_bucket_name,
        replace=True
    )

@task
def upload_message()-> None:
    logging.info("Upload complete!")
    

default_args = {
    'owner': 'airflow',
    'catchup': False,
    'start_date': datetime(2023, 9, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
    'max_active_tasks' : 5
}

with DAG(
    'async_workbook_scraper',
    default_args=default_args,
    description='A async workbook scraper DAG',
    schedule_interval='0 3 * * 3',
) as dag:
    
    url = "https://www.acmicpc.net/workbook"
    flag = 'workbook'

    start, end = 1, 20
    scraper_objects = scrape_workbook_user(url, start, end, flag)
    save_to_csv_task = save_to_csv(scraper_object=scraper_objects, flag=flag)
    
    s3_bucket_name = 'baekjoon-data'
    s3_folder = 'workbooks/'
    
    data_dir = os.environ.get('AIRFLOW_VAR_DATA_DIR')
    
    # data_folder = os.path.join(os.getcwd(), "data")
    csv_file = os.path.join(data_dir, 'workbooks.csv')
    file_name = os.path.basename(csv_file)
    s3_key = os.path.join(s3_folder, file_name)

    s3_hook = S3Hook(aws_conn_id='aws_default')
    upload_task = upload_local_file_to_s3(csv_file=csv_file, s3_key=s3_key, s3_bucket_name=s3_bucket_name, s3_hook=s3_hook) 
    
    upload_message_task = upload_message()
    
    scraper_objects >> save_to_csv_task >> upload_task >> upload_message_task
    

