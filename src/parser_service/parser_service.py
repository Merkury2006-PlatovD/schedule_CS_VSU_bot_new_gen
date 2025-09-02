from logging import Logger
from os import environ

from src.authentication_service.model.model import UserDTO
from src.authentication_service.db.redis_repo import RedisDatabase
from src.parser_service.excell_converter import ScheduleParser
from src.parser_service.excell_loader import download_and_update
from src.parser_service.util.error import ParserError
from src.tools.logger import set_up_logger


class ParserService:
    __logger: Logger
    __redis_db: RedisDatabase
    __parser: ScheduleParser

    def __init__(self, parser: ScheduleParser, redis: RedisDatabase):
        self.__parser = parser
        self.__logger = set_up_logger('./log/parser_service.log')
        self.__redis_db = redis

    def get_schedule_on_day(self, user: UserDTO, day: int, week=None):
        week = self.__redis_db.get_week_type() if week is None else week
        try:
            (course, main_group, sub_group) = user.get_course(), user.get_main_group(), user.get_sub_group()
            column = self.__parser.find_required_col(course, main_group, sub_group)
            schedule = self.__parser.get_lessons_on_day(column, day, week)
            return schedule
        except ParserError as err:
            raise err

    def refresh_parser(self):
        self.__parser.refresh_workbook()

    def refresh_schedule(self):
        download_and_update()
        self.refresh_parser()
