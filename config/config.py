from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config(BaseSettings):
    mongo_connection: str = getenv("MONGO_CONNECTION")
    db_name: str = getenv("MONG0_DATABASE")
    qa_collection: str = getenv("MONGO_QA_COLLECTION")
    users_collection: str = getenv("MONGO_USERS_COLLECTION")
    secret: str = getenv("SECRET_KEY")


@lru_cache()
def get_config():
    return Config()
