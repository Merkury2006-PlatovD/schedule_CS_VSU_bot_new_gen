from logging import Logger

from redis import Redis

from src.authentication_service.db.model import UserDTO
from src.parser_service.excell_converter import ScheduleParser
from src.parser_service.util.error import ParserError
from src.tools_wrappers.logger import set_up_logger
from src.tools_wrappers.redis_repo import RedisDatabase
from src.tools_wrappers.redis_wrapper import RedisWrapper


class ParserService:
    __logger: Logger
    __redis: Redis
    __parser: ScheduleParser

    def __init__(self, parser):
        self.__parser = parser
        self.__logger = set_up_logger('./log/parser_service.log')
        self.__redis = RedisWrapper.get_redis()

    def get_schedule_on_day(self, user: UserDTO, day: int, week=None):
        week = RedisDatabase.get_week_type() if week is None else week
        try:
            (course, main_group, sub_group) = user.get_course(), user.get_main_group(), user.get_sub_group()
            column = self.__parser.find_required_col(course, main_group, sub_group)
            schedule = self.__parser.get_lessons_on_day(column, day, week)
            return schedule
        except ParserError as err:
            raise err
