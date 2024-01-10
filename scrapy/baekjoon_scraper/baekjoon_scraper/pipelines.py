# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from collections import defaultdict
from sqlalchemy import create_engine, Table, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
import polars as pl
from baekjoon_scraper.config import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
import pandas as pd
import logging


class RDSPipeline:
    def __init__(self):
        self.items = defaultdict(list)
        self.engine = None
        self.operation_modes = {
            'problems': 'full_refresh',
            'users': 'full_refresh',
            'workbooks': 'full_refresh',
            'problem_details': 'full_refresh',
            'problem_texts': 'full_refresh',
            'user_details': 'upsert',
            'user_results': 'upsert',
        }

    def open_spider(self, spider):
        try:
            self.engine = self.init_db()
            logging.info('Database engine connected')
        except SQLAlchemyError as e:
            logging.error(f'Database connection error: {e}')
            raise

    def close_spider(self, spider):
        logging.info('Processing data at the end of spider run')
        for item_type, items in self.items.items():
            table_name, _ = self.get_table_info(item_type)
            if table_name in self.operation_modes:
                self.process_batch(item_type, items)
            else:
                logging.error(f"Unknown item type: {item_type}. Skipping batch processing.")

        self.dispose_db_connection()

    def process_item(self, item, spider):
        item_type = type(item).__name__
        table_name, index_columns = self.get_table_info(item_type)

        # Check for None return from get_table_info
        if not table_name or not index_columns:
            logging.error(f"Missing table information for item type: {item_type}.")
            return item

        operation_mode = self.operation_modes.get(table_name, 'full_refresh')

        if operation_mode == 'upsert':
            self.upsert_single_item(item, table_name, index_columns)
        else:
            self.items[item_type].append(item)

        return item

    def full_refresh_data(self, items, table_name, index_columns):

        sorted_items = sorted(items, key=lambda i: i[index_columns[0]])
        df = pd.DataFrame(sorted_items)
        df.set_index(index_columns, inplace=True)
        self.full_refresh(df, table_name)

    def process_batch(self, item_type, items):
        table_name, index_columns = self.get_table_info(item_type)
        if not table_name or not index_columns:
            logging.error(f"Missing table information for item type: {item_type}.")
            return

        df = pd.DataFrame(items)
        df.set_index(index_columns, inplace=True)

        operation_mode = self.operation_modes.get(table_name, 'full_refresh')
        if operation_mode == 'full_refresh':
            self.full_refresh(df, table_name)
        else:
            logging.warning(f"Unsupported operation mode: {operation_mode} for item type: {item_type}.")

    def full_refresh(self, df, table_name):
        try:
            with self.engine.begin() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                df.to_sql(table_name, con=conn, index=True)
                self.set_primary_key(table_name, conn)
            logging.info(f'Table {table_name} refreshed successfully')
        except SQLAlchemyError as e:
            logging.error(f'Full refresh error: {e}')

    def upsert_single_item(self, item, table_name, index_columns):
        adapter = ItemAdapter(item)
        record = adapter.asdict()

        pk_columns_list = self.get_primary_key_column(table_name).split(', ')

        # Convert list values to PostgreSQL array format
        for key, value in record.items():
            if isinstance(value, list):
                record[key] = '{' + ', '.join([str(v) for v in value]) + '}'

        try:
            with self.engine.connect() as conn:
                # Construct the insert statement
                stmt = insert(Table(table_name, MetaData(), autoload_with=self.engine)).values(record)
                # Add the on_conflict clause
                do_update_stmt = stmt.on_conflict_do_update(
                    index_elements=pk_columns_list,
                    set_={col: getattr(stmt.excluded, col) for col in record.keys()}
                )
                # Execute the statement
                result = conn.execute(do_update_stmt)
                conn.commit()

                logging.info(f"{result.inserted_primary_key} pk inserted")
        except SQLAlchemyError as e:
            logging.error(f'Failed to upsert item: {str(e)}')

    def set_primary_key(self, table_name, conn):
        pk_column = self.get_primary_key_column(table_name)
        if pk_column:
            try:
                conn.execute(text(f"ALTER TABLE {table_name} ADD PRIMARY KEY ({pk_column})"))
            except SQLAlchemyError as e:
                logging.error(f'Primary key error: {e}')

    def get_table_info(self, item_type):
        # Mapping from item types to database table names and index columns
        mapping = {
            'ProblemItem': ('problems', ['problem_id']),
            'UserItem': ('users', ['user_id']),
            'WorkbookItem': ('workbooks', ['workbook_id', 'problem_id']),
            'ProblemDetailItem': ('problem_details', ['problem_id', 'problem_level', 'tag_key']),
            'ProblemTextItem': ('problem_texts', ['problem_id', 'problem_title']),
            'UserDetailItem': ('user_details', ['user_id', 'user_tier']),
            'UserResultItem': ('user_results', ['user_id']),
        }

        return mapping.get(item_type, (None, None))

    def get_primary_key_column(self, table_name):
        # Mapping from table names to primary key columns
        mapping = {
            'problems': 'problem_id',
            'users': 'user_id',
            'workbooks': 'workbook_id, problem_id',
            'problem_details': 'problem_id, problem_level, tag_key',
            'problem_texts': 'problem_id, problem_title',
            'user_details': 'user_id, user_tier',
            'user_results': 'user_id',
        }

        return mapping.get(table_name, None)


    @staticmethod
    def init_db():
        try:
            username = config.DB_USER
            password = config.DB_PASSWORD
            host = config.DB_HOST
            port = config.DB_PORT
            database = config.DB_NAME
            engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
            return engine
        except SQLAlchemyError as e:
            logging.error(f'Error initializing database: {str(e)}')
            raise

    def dispose_db_connection(self):
        if self.engine:
            self.engine.dispose()
            logging.warning('Database connection disposed')
