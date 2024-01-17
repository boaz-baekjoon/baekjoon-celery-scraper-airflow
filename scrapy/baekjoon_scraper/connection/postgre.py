from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from config.config import config

engines = {
    "baekjoon": create_engine(
        URL.create(
            drivername="postgresql",
            username=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME
        ),
        pool_recycle=3600
    )
}

Base = declarative_base()


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kw):
        bind_key = mapper.class_.__bind_key__ if mapper else None
        return engines[bind_key] if bind_key in engines else None


postgre_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engines['baekjoon'], class_=RoutingSession)
)


def get_postgre_db():
    db = postgre_session()
    try:
        yield db
    finally:
        db.close()
