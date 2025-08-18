from fastapi import FastAPI, Response
from starlette import status
from starlette.config import environ
from telebot import TeleBot

from src.authentication_service.authentification_service import AuthenticationService
from src.authentication_service.db.model import UserDTO
from src.authentication_service.db.mysql_repo import DataBase
from src.parser_service.excell_converter import ScheduleParser
from src.parser_service.parser_service import ParserService
from src.tools_wrappers.redis_repo import RedisDatabase
from src.tools_wrappers.scheduler_wrapper import SchedulerWrapper


def create_configured_bot() -> TeleBot:
    bot_ex = TeleBot(environ.get('BOT_TOKEN'))
    bot_ex.set_webhook(environ.get('WEBHOOK'))
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


# # setting handlers for bot
# bot_controller = BotController(
#     bot,
#     parser_service,
#     authentication_service,
#     RedisWrapper.get_redis(),
#     set_up_logger('./log/bot_controller.log')
# )


@app.post('/api/schedule/{token}/{course}/{group}/{subgroup}/{day}')
def get_schedule(token: str, course: int, group: int, subgroup: int, day: int, response: Response):
    print(token)
    if not authentication_service.has_key(token):
        response.status = status.HTTP_401_UNAUTHORIZED
        return 'fuck'

    print(course, group, subgroup)
    print(RedisDatabase.get_week_type())
    return parser_service.get_schedule_on_day(UserDTO(0, course, group, subgroup), day, RedisDatabase.get_week_type())
