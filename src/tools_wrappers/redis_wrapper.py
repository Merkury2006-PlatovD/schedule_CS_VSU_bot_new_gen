from os import environ

import redis
from redis import Redis


class RedisWrapper:
    __redis = redis.StrictRedis(
        host=environ.get('REDIS_HOST'),
        port=int(environ.get('REDIS_PORT')),
        encoding='utf-8',
        decode_responses=True,
    )
    USER_SAVING_DURATION = int(environ.get('REDIS_USER_DATA_SAVE_DURATION'))

    @classmethod
    def get_redis(cls) -> Redis:
        return cls.__redis
