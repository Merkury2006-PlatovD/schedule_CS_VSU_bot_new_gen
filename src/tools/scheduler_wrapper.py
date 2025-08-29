from apscheduler.schedulers.background import BackgroundScheduler

from src.parser_service.excell_loader import download_and_update
from src.authentication_service.db.redis_repo import RedisDatabase


class SchedulerWrapper:
    __scheduler = BackgroundScheduler()
    __redis_db: RedisDatabase

    @classmethod
    def set_redis_db(cls, redis_db: RedisDatabase):
        cls.__redis_db = redis_db

    @classmethod
    def init(cls):
        cls.__scheduler.add_job(download_and_update, 'interval', minutes=30)
        cls.__scheduler.add_job(cls.__redis_db.change_week_type, 'cron', day_of_week=5, hour=20, minute=0, second=0)

    @classmethod
    def on_start(cls):
        download_and_update()
        cls.__scheduler.start()

    @classmethod
    def get_day_from_num(cls, day: int):
        days = {
            0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье"
        }
        return days.get(day)
