from os import environ
from typing import Any

from src.authentication_service.util.interface import DatabaseConnectable
import redis
from redis import Redis


class RedisConnector(DatabaseConnectable):
    __db: Redis | None = None

    @classmethod
    def get_connection(cls) -> Any:
        return cls.__db

    @classmethod
    def init_connection(cls) -> None:
        cls.__db = redis.StrictRedis(
            host=environ.get('REDIS_HOST'),
            port=int(environ.get('REDIS_PORT')),
            encoding='utf-8',
            decode_responses=True,
            retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError]
        )

    @classmethod
    def close_connection(cls) -> None:
        cls.__db.close()

    @classmethod
    def reconnect(cls) -> None:
        cls.__db = None
        cls.init_connection()
