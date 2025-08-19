from logging import Logger
from os import environ

import telebot

from fastapi import APIRouter, status, Response, Request, HTTPException

from src.authentication_service.authentification_service import AuthenticationService
from src.authentication_service.db.model import UserDTO
from src.parser_service.parser_service import ParserService
from src.tools_wrappers.redis_repo import RedisDatabase
from src.tools_wrappers.scheduler_wrapper import SchedulerWrapper


class APIController:
    __bot: telebot.TeleBot
    __router: APIRouter
    __parser_service: ParserService
    __authentication_service: AuthenticationService
    __logger: Logger

    def __init__(self, bot, parser_service, authentication_service, logger):
        self.__bot = bot
        self.__router = APIRouter()
        self.__parser_service = parser_service
        self.__authentication_service = authentication_service
        self.__logger = logger

    def start_controller(self):
        self.set_handlers()

    def set_handlers(self):
        @self.__router.post('/api/schedule/{token}/{course}/{group}/{subgroup}/{day}')
        def get_schedule(token: str, course: int, group: int, subgroup: int, day: int, response: Response):
            if not self.__authentication_service.has_key(token):
                response.status = status.HTTP_401_UNAUTHORIZED

            return {
                'course': course,
                'group': group,
                'sub_group': subgroup,
                'day': SchedulerWrapper.get_day_from_num(day),
                'schedule': self.__parser_service.get_schedule_on_day(UserDTO(0, course, group, subgroup), day,
                                                                      RedisDatabase.get_week_type()),
            }

        @self.__router.post(environ.get("WEBHOOK_URL"))
        async def process_webhook(request: Request):
            try:
                raw_data = await request.body()
                json_data = raw_data.decode('utf-8')
                update = telebot.types.Update.de_json(json_data)
                self.__bot.process_new_updates([update])
                return {'status': 'ok'}
            except Exception as err:
                print(err)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err)

    def get_router(self):
        return self.__router
