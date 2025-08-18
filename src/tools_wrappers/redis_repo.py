from src.tools_wrappers.redis_wrapper import RedisWrapper


class RedisDatabase:
    __redis = RedisWrapper.get_redis()

    @classmethod
    def get_week_type(cls) -> int:
        week_type = cls.__redis.get("var:week_type")
        if week_type is None:
            cls.__redis.set("var:week_type", 0)
            return 0
        else:
            return int(week_type)

    @classmethod
    def change_week_type(cls):
        week_type = cls.get_week_type()
        if week_type == 0:
            cls.__redis.set("var:week_type", 1)
        else:
            cls.__redis.set("var:week_type", 0)

    @classmethod
    def set_users_per_day(cls, count: int):
        cls.__redis.set("var:users_per_day", count)

    @classmethod
    def get_users_per_day(cls):
        return int(cls.__redis.get("var:users_per_day"), 0)

    @classmethod
    def increment_users_per_day(cls):
        cls.__redis.incrby("var:users_per_day", 1)

    @classmethod
    def get_from_redis(cls, key: str):
        return cls.__redis.get(key)
