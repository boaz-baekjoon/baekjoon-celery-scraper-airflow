from sqlalchemy import create_engine, Table, MetaData, text
from config.config import config


def init_db():
    username = config.DB_USER
    password = config.DB_PASSWORD
    host = config.DB_HOST
    port = config.DB_PORT
    database = config.DB_NAME
    engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
    return engine


engine = init_db()
