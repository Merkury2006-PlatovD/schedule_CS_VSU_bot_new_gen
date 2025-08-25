import json
import os
import time

from redis import Redis
import redis

from src.authentication_service.model.model import RequestDTO
from src.tools.logger import set_up_logger

"""
Используется три бд:
  - api: для хранение пар пользователь-ключ
  - user: для хранения json UserDTO model 
  - var: для хранения переменных, используемых в работе парсера
  - request: для хранения данных о запросах и защите от нагрузочных атак
"""


class RedisDatabase:
    __instance = None

    __redis: Redis
    __logger = set_up_logger('./log/redis_db.log')
    __refill_interval: int = int(os.getenv("TOKEN_REFILL_INTERVAL_SEC"))

    def __init__(self, redis_init):
        self.__redis = redis_init

    def get_from_cache(self, db: str, key: int | str):
        return self.__redis.get(f"{db}:{key}")

    def set_cache(self, db: str, key: int | str, value: int | str | bool | bytes, exp=None):
        if exp is not None:
            self.__redis.set(f"{db}:{key}", value, exp)
            return
        self.__redis.set(f"{db}:{key}", value)

    def delete_from_cache(self, db: str, key: int | str):
        try:
            self.__redis.delete(f"{db}:{key}")
        except redis.RedisError as err:
            self.__logger.warning("Redis failed to delete data cache. %s", err)

    def check_requests_rate(self, user_id: int) -> bool:
        cur_time = time.time()
        raw_data = self.get_from_cache(db="request", key=user_id)

        if raw_data is None:
            request = RequestDTO(user_id, int(cur_time), 4)
            self.set_cache(db="request", key=user_id, value=request.get_data_json(),
                           exp=int(self.__refill_interval * 2))
            return True

        request = RequestDTO.create_from_json(raw_data)
        if cur_time - request.get_timing() < self.__refill_interval:
            request.decrease_tokens()
        else:
            request.set_tokens(5)
        request.set_timing(cur_time)
        self.set_cache(db="request", key=user_id, value=request.get_data_json(),
                       exp=int(self.__refill_interval * 2))
        return request.get_tokens() > 0

    def get_week_type(self) -> int:
        week_type = self.__redis.get("var:week_type")
        if week_type is None:
            self.__redis.set("var:week_type", 0)
            return 0
        else:
            return int(week_type)

    def change_week_type(self):
        week_type = self.get_week_type()
        if week_type == 0:
            self.__redis.set("var:week_type", 1)
        else:
            self.__redis.set("var:week_type", 0)

    def set_users_per_day(self, count: int):
        self.__redis.set("var:users_per_day", count)

    def get_users_per_day(self):
        return int(self.__redis.get("var:users_per_day"))

    def increment_users_per_day(self):
        self.__redis.incrby("var:users_per_day", 1)
