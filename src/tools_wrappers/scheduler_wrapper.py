from apscheduler.schedulers.background import BackgroundScheduler

from src.parser_service.excell_loader import download_and_update
from src.tools_wrappers.redis_repo import RedisDatabase


class SchedulerWrapper:
    __scheduler = BackgroundScheduler()

    @classmethod
    def init(cls):
        cls.__scheduler.add_job(download_and_update, 'interval', minutes=30)
        cls.__scheduler.add_job(RedisDatabase.change_week_type, 'cron', day_of_week=5, hour=20, minute=0, second=0)

    @classmethod
    def on_start(cls):
        download_and_update()
