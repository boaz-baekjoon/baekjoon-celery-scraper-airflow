from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.S3_hook import S3Hook
from airflow.hooks.postgres_hook import PostgresHook

default_args = {
    'owner': 'yoohajun',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    's3_to_postgres',
    default_args=default_args,
    description='Load CSV from S3 to Postgres',
    schedule_interval='@once',
    start_date=datetime(2023, 9, 1),
    catchup=False
)

def drop_table_if_exists(postgres, table_name):
    drop_table_query = f"""
    DROP TABLE IF EXISTS {table_name};
    """
    postgres.run(drop_table_query)

def create_and_load_table(postgres, table_name, header):
    # Assuming all columns are of type TEXT for simplicity
    columns_with_types = ', '.join([f"{col} TEXT" for col in header])
    create_table_query = f"""
    CREATE TABLE {table_name} ({columns_with_types});
    """
    postgres.run(create_table_query)

def transfer_s3_to_postgres():
    s3 = S3Hook('aws_default')
    postgres = PostgresHook('postgres_conn_id')

    # Get your data from S3
    s3_key = 'problems/problems.csv'
    s3_bucket = 'baekjoon-data'
    file_obj = s3.get_key(s3_key, s3_bucket)
    csv_content = file_obj.get()['Body'].read().decode('utf-8')

    # Assuming your CSV has a header and is comma-separated
    rows = csv_content.strip().split('\n')
    header = rows[0].split(',')
    data = [row.split(',') for row in rows[1:]]

    table_name = "your_table_name"
    
    # Drop table if it exists
    drop_table_if_exists(postgres, table_name)

    # Create new table and load data
    create_and_load_table(postgres, table_name, header)

    # Insert data into PostgreSQL
    for row in data:
        placeholders = ', '.join(['%s' for item in row])
        insert_query = f"INSERT INTO {table_name} ({','.join(header)}) VALUES ({placeholders});"
        postgres.run(insert_query, parameters=row)

transfer_task = PythonOperator(
    task_id='transfer_s3_to_postgres',
    python_callable=transfer_s3_to_postgres,
    dag=dag
)

transfer_task