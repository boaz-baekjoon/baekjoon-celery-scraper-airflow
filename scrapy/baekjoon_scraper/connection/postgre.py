from sqlalchemy import create_engine, Table, MetaData, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

def init_db():
    username = config.DB_USER
    password = config.DB_PASSWORD
    host = config.DB_HOST
    port = config.DB_PORT
    database = config.DB_NAME
    engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
    return engine