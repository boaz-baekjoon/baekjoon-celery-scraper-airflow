import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class DBConfig:
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = os.environ["DB_PORT"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_NAME = os.environ["DB_NAME"]


class RedisConfig:
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = os.environ["REDIS_PORT"]
    pass


class Config(
    RedisConfig,
    DBConfig
):
    pass


@lru_cache()
def get_config():
    config_cls_dict = {
        "production": Config,
    }
    config_name = os.getenv("MY_APP_CONFIG", "production")
    return config_cls_dict[config_name]()


config = get_config()
