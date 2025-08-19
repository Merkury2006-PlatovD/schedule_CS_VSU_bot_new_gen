from fastapi import FastAPI
from starlette.config import environ
from telebot import TeleBot
from fastapi.middleware.cors import CORSMiddleware
from src.authentication_service.authentification_service import AuthenticationService
from src.authentication_service.db.mysql_repo import DataBase
from src.controller_api import APIController
from src.controller_bot import BotController
from src.parser_service.excell_converter import ScheduleParser
from src.parser_service.parser_service import ParserService
from src.tools_wrappers.logger import set_up_logger
from src.tools_wrappers.scheduler_wrapper import SchedulerWrapper


def create_configured_bot() -> TeleBot:
    bot_ex = TeleBot(environ.get('BOT_TOKEN'))
    bot_ex.set_webhook(environ.get('WEBHOOK_DOMAIN') + environ.get("WEBHOOK_URL"))
    return bot_ex


# bot = create_configured_bot()
app = FastAPI()

# connect to mysql (init connection is inside auth service)
db = DataBase()

# starting updaters (need to create reseter for users_per_day)
SchedulerWrapper.init()
SchedulerWrapper.on_start()

# start parser service
parser_service = ParserService(ScheduleParser(environ.get('MAIN_SCHEDULE_PATH')))

# starting auth servie and init connection to db
authentication_service = AuthenticationService(db)
authentication_service.start_service()

bot = create_configured_bot()

# setting handlers for bot
bot_controller = BotController(
    bot,
    parser_service,
    authentication_service,
    set_up_logger('./log/bot_controller.log')
)
bot_controller.start_controller()

# setting handlers for api
api_controller = APIController(
    bot,
    parser_service,
    authentication_service,
    set_up_logger('./log/api_controller.log')
)
api_controller.start_controller()
app.include_router(api_controller.get_router())

origins = ["*"]
