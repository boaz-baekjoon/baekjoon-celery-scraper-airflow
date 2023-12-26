from dotenv import load_dotenv
import os

load_dotenv()


class DBConfig:
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = os.environ["DB_PORT"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_NAME = os.environ["DB_NAME"]


class ProxyConfig:
    PROXY_SERVER_IP = os.environ["PROXY_SERVER_IP"]


class RedisConfig:
    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = os.environ["REDIS_PORT"]


class Config(DBConfig, ProxyConfig, RedisConfig):
    pass


config = Config()
