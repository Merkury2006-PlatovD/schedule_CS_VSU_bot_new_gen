from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any

from fastapi import FastAPI
from starlette.config import environ
from telebot import TeleBot

from src.authentication_service.authentification_service import AuthenticationService
from src.authentication_service.connector.db_connector import DBConnector
from src.authentication_service.connector.redis_connector import RedisConnector
from src.authentication_service.db.mysql_repo import DataBase
from src.authentication_service.db.redis_repo import RedisDatabase
from src.controller_api import APIController
from src.controller_bot import BotController
from src.parser_service.excell_converter import ScheduleParser
from src.parser_service.parser_service import ParserService
from src.tools.logger import set_up_logger
from src.tools.scheduler_wrapper import SchedulerWrapper


def create_configured_bot() -> TeleBot:
    bot_ex = TeleBot(environ.get('BOT_TOKEN'))
    bot_ex.set_webhook(environ.get('WEBHOOK_DOMAIN') + environ.get("WEBHOOK_URL"))
    return bot_ex


logger = set_up_logger('log/main.log')


@asynccontextmanager
async def lifespan(app_fastAPI: FastAPI) -> AsyncIterator[Dict[str, Any]]:
    try:
        # initialize connections
        RedisConnector.init_connection()
        DBConnector.init_connection()

        # DI connections into data change classes
        db = DataBase(connection=DBConnector.get_connection())
        redis_db = RedisDatabase(redis_init=RedisConnector.get_connection())

        # starting updaters (need to create resetter for users_per_day)
        SchedulerWrapper.set_redis_db(redis_db)
        SchedulerWrapper.init()
        SchedulerWrapper.on_start()

        # start parser service
        parser_service = ParserService(parser=ScheduleParser(environ.get('MAIN_SCHEDULE_PATH')), redis=redis_db)

        # starting auth service
        authentication_service = AuthenticationService(database=db, redis_init=redis_db)

        bot = create_configured_bot()

        # setting handlers for bot
        bot_controller = BotController(
            bot=bot,
            parser_service=parser_service,
            authentication_service=authentication_service,
            redis_db=redis_db,
            logger=set_up_logger('./log/bot_controller.log')
        )
        bot_controller.start_controller()

        # setting handlers for api
        api_controller = APIController(
            bot=bot,
            parser_service=parser_service,
            authentication_service=authentication_service,
            redis_db=redis_db,
            logger=set_up_logger('./log/api_controller.log'),
        )
        api_controller.start_controller()
        app_fastAPI.include_router(api_controller.get_router())
        yield {}
    except Exception as err:
        print("Error during running application. %s", err)


app = FastAPI(lifespan=lifespan)
