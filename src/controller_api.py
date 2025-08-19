from logging import Logger
from os import environ
import telebot

from fastapi import APIRouter, status, Response

from src.authentication_service.authentification_service import AuthenticationService
from src.authentication_service.db.model import UserDTO
from src.parser_service.parser_service import ParserService
from src.tools_wrappers.redis_repo import RedisDatabase


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

            return self.__parser_service.get_schedule_on_day(UserDTO(0, course, group, subgroup), day,
                                                             RedisDatabase.get_week_type())

        @self.__router.post(environ.get("WEBHOOK_URL"))
        def process_webhook(update: dict):
            if update:
                update = telebot.types.Update.de_json(update)
                self.__bot.process_new_updates(update)

    def get_router(self):
        return self.__router
