from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    PROXY_SERVER_IP = os.environ["PROXY_SERVER_IP"]


config = Config()
