import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()


class RedisConfig:
    celery_broker_url = os.getenv("CELERY_BROKER_URL")
    celery_result_backend = os.getenv("CELERY_RESULT_BACKEND")
    pass


class Config(
    RedisConfig,
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
