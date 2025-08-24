from logging import Logger

import telebot
from telebot.types import Message

from src.authentication_service.authentification_service import AuthenticationService
from src.authentication_service.util.enum import UpdateType
from src.authentication_service.util.error import APIError
from src.parser_service.parser_service import ParserService
from src.parser_service.util.error import ScheduleParserFindError
from src.tools.keyboard_generators import *
from src.authentication_service.db.redis_repo import RedisDatabase


class BotController:
    __bot: telebot.TeleBot
    __parser_service: ParserService
    __authentication_service: AuthenticationService
    __redis_db: RedisDatabase
    __logger: Logger

    def __init__(self, bot, parser_service, authentication_service, redis_db: RedisDatabase, logger):
        self.__bot = bot
        self.__parser_service = parser_service
        self.__authentication_service = authentication_service
        self.__redis_db = redis_db
        self.__logger = logger

    def start_controller(self):
        self.set_handlers()

    def set_handlers(self):
        def set_bot_commands_menu():
            self.__bot.set_my_commands([
                telebot.types.BotCommand("start", "Начать работу с ботом"),
                telebot.types.BotCommand("help", "Получить помощь"),
                telebot.types.BotCommand("info", "Узнать информацию о себе"),
                telebot.types.BotCommand("updateinfo", "Поменять информацию о себе"),
                telebot.types.BotCommand("mistake", "Сообщить об ошибке в расписании"),
                telebot.types.BotCommand("znam", "Посмотреть расписание на знаменатель"),
                telebot.types.BotCommand("chis", "Посмотреть расписание на числитель"),
                telebot.types.BotCommand("getapi", "Получить API-токен"),
                telebot.types.BotCommand("deleteapi", "Удалить API-токен")
            ])

        @self.__bot.message_handler(commands=['start'])
        def handle_start(message):
            """
            Слушает команду "/start" и выполняет действия в зависимости от результата user_exists(user_id). Начинает работу всего бота.

            Args:
                message: экземпляр telebot.types.Message.
            """
            set_bot_commands_menu()
            user_id = message.from_user.id
            try:
                user_exists = self.__authentication_service.has_user(user_id)
                if not user_exists:
                    self.__authentication_service.add_user(user_id)
                    self.__bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())
                else:
                    self.__bot.send_message(user_id, "Ты уже зарегистрирован!")
                    self.__bot.send_message(user_id, "На какой день тебе нужно расписание?",
                                            reply_markup=get_persistent_keyboard())
            except Exception as err:
                handle_error(user_id, err, "Ошибка обработки команды /start")

        @self.__bot.message_handler(commands=['updateinfo'])
        def handle_profile_update(message):
            """
            Слушает команду "/updateinfo" и регистрирует/изменяет данные о пользователе в БД.

            Args:
                message: экземпляр telebot.types.Message.
            """
            user_id = message.from_user.id
            try:
                if not self.__authentication_service.has_user(user_id):
                    self.__authentication_service.add_user(user_id)
                self.__bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())
            except Exception as err:
                handle_error(user_id, err, "Ошибка обработки команды /updateinfo")

        @self.__bot.message_handler(commands=['help'])
        def handle_help(message):
            """
            Слушает команду "/help" и выводит пользователю справочную информацию.

            Args:
                message: экземпляр telebot.types.Message.
            """
            self.__bot.send_message(message.from_user.id, "Привет! Я помогу тебе с расписанием: \n"
                                                          "•  Напиши команду /start, чтобы я узнал информацию о тебе и твоем расписании\n"
                                                          "•  Напиши команду /updateinfo, чтобы изменить информацию о тебе\n"
                                                          "•  Напиши команду /info, чтобы узнать краткую информацию о тебе\n"
                                                          "•  Напиши команду /mistake, чтобы отправить отчет о неправильном расписании\n"
                                                          "•  Напиши команду /znam, чтобы посмотреть расписание на знаменатель\n"
                                                          "•  Напиши команду /chis, чтобы посмотреть расписание на числитель")

        @self.__bot.message_handler(commands=['info'])
        def handle_info(message):
            user_id = message.from_user.id
            try:
                user = self.__authentication_service.get_user(user_id)
                self.__bot.send_message(message.from_user.id, "Информация о тебе: \n"
                                                              f"Твой курс: {user.get_course()}\n"
                                                              f"Твоя группа: {user.get_main_group()}\n"
                                                              f"Твоя подгруппа: {user.get_sub_group()}")
            except Exception as err:
                handle_error(user_id, err, "Ошибка обработки команды /info")

        @self.__bot.message_handler(commands=['mistake'])
        def handle_mistake_report(message):
            self.__bot.send_message(message.from_user.id,
                                    "Подтвердите факт ошибки в расписании. Если ошибок нет, просим вас не создавать нам лишней работы!",
                                    reply_markup=get_mistake_report_keyboard())

        @self.__bot.message_handler(commands=['getUsersPerDay'])
        def handle_users_per_day_request(message):
            self.__bot.send_message(message.from_user.id,
                                    f"Запросов за текущий день {self.__redis_db.get_users_per_day()}")

        @self.__bot.message_handler(commands=['chis', 'znam'])
        def handle_chis_znam_schedule(message):
            user_id = message.from_user.id
            print(f"Запрос от {user_id}: {message.from_user.username}")
            self.__redis_db.increment_users_per_day()

            try:
                if not self.__authentication_service.has_user(user_id):
                    self.__authentication_service.add_user(user_id)
                    self.__bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())
                else:
                    try:
                        out_data_formated = f"Твое расписание на {"числитель" if message.text == '/chis' else 'знаменатель'}:\n\n"
                        days_map = {"📅 Понедельник": 0, "📅 Вторник": 1, "📅 Среда": 2, "📅 Четверг": 3, "📅 Пятница": 4,
                                    "📅 Суббота": 5}
                        user = self.__authentication_service.get_user(user_id)
                        week = 0 if message.text == '/chils' else 1

                        for key, val in days_map.items():
                            schedule = self.__parser_service.get_schedule_on_day(user, val, week=week)
                            out_data_formated += f"📅 *Расписание занятий на {key.split(' ')[-1]}:*\n\n"
                            for key_day, val_day in schedule.items():
                                if val_day is None or val_day.strip() == "":
                                    val_day = "— Нет пары —"
                                out_data_formated += f"🕒 *{key_day}*\n📖 {val_day}\n\n"

                        self.__bot.send_message(user_id, out_data_formated, parse_mode="Markdown")
                    except (ScheduleParserFindError, TypeError, ValueError) as e:
                        handle_error(user_id, e,
                                     "Возможно ошибка связана с обновлением на сервере. В таком случае просим Вас просто заново ввести данные. Мы сделам все возможное, чтобы это не повторилось.\n\n❌ Мы не смогли найти учебную группу с вашими данными.\n🔍 Убедитесь, что вы правильно ввели все данные.\n💡 Попробуйте ввести их еще раз.")
                        handle_profile_update(message)
            except Exception as err:
                handle_error(user_id, err, "Ошибка обработки запроса расписания на неделю")

        @self.__bot.message_handler(commands=['getapi'])
        def handle_api_get(message: Message):
            user_id = message.from_user.id
            try:
                api_key = self.__authentication_service.add_new_api_key(user_id)
                self.__bot.send_message(user_id, f"Your API key:\n{api_key}")
            except APIError as err:
                handle_error(user_id, err,
                             "Ошибка создания API ключа. Убедитесь, что он не был создан до настоящего времени")

        @self.__bot.message_handler(commands=['deleteapi'])
        def handle_api_key_delete(message: Message):
            user_id = message.from_user.id
            try:
                self.__authentication_service.remove_api_key(user_id)
                self.__bot.send_message(user_id, "Ключ API успешно удален! Вы можете создать новый командой getapi")
            except Exception as err:
                handle_error(user_id, err, 'Ошибка удаления API')

        @self.__bot.message_handler(
            func=lambda message: message.text not in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница",
                                                      "📅 Суббота"])
        def handle_error_message(message):
            user_id = message.from_user.id
            self.__bot.send_message(user_id,
                                    "Привет! Напиши /start для запуска бота или /help для более подробной информации")

        @self.__bot.message_handler(
            func=lambda message: message.text in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница",
                                                  "📅 Суббота"])
        def handle_schedule_request(message):
            days_map = {"📅 Понедельник": 0, "📅 Вторник": 1, "📅 Среда": 2, "📅 Четверг": 3, "📅 Пятница": 4,
                        "📅 Суббота": 5}
            user_id = message.from_user.id
            print(f"Запрос от {user_id}: {message.from_user.username}")
            self.__redis_db.increment_users_per_day()
            day = days_map[message.text]
            try:
                week_type = self.__redis_db.get_week_type()
                user = self.__authentication_service.get_user(user_id)
                schedule = self.__parser_service.get_schedule_on_day(user, day)
                out_data_formated = f"📅 *Расписание занятий на {message.text.split(' ')[-1]}/{'числ' if week_type == 0 else 'знам'}:*\n\n"

                for key, val in schedule.items():
                    if val is None or val.strip() == "":
                        val = "— Нет пары —"

                    out_data_formated += f"🕒 *{key}*\n📖 {val}\n\n"

                self.__bot.send_message(user_id, out_data_formated, parse_mode="Markdown")
            except (ScheduleParserFindError, TypeError, ValueError) as e:
                handle_error(user_id, e,
                             "Возможно ошибка связана с обновлением на сервере. В таком случае просим Вас просто заново ввести данные. Мы сделам все возможное, чтобы это не повторилось.\n\n❌ Мы не смогли найти учебную группу с вашими данными.\n🔍 Убедитесь, что вы правильно ввели все данные.\n💡 Попробуйте ввести их еще раз.")
                handle_profile_update(message)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
        def handle_course(call):
            user_id = call.from_user.id
            course = int(call.data.split("_")[1])

            self.__authentication_service.update_user_data(UpdateType.course, user_id, course)
            keyboard = get_group_keyboard()
            self.__bot.send_message(user_id, "Теперь выбери свою группу:", reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
        def handle_group(call):
            user_id = call.from_user.id
            group = int(call.data.split("_")[1])

            self.__authentication_service.update_user_data(UpdateType.main_group, user_id, group)
            keyboard = get_subgroup_keyboard()
            self.__bot.send_message(user_id, "Теперь выбери свою подгруппу:", reply_markup=keyboard)

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith("subgroup_"))
        def handle_subgroup(call):
            user_id = call.from_user.id
            subgroup = int(call.data.split("_")[-1])

            self.__authentication_service.update_user_data(UpdateType.sub_group, user_id, subgroup)
            self.__bot.send_message(user_id, "Отлично! Данные сохранены.")
            self.__bot.send_message(user_id, "На какой день тебе нужно расписание?",
                                    reply_markup=get_persistent_keyboard())

        @self.__bot.callback_query_handler(func=lambda call: call.data.startswith("mistake"))
        def handle_report_send(call):
            if call.data.split("_")[-1] == "1":
                user = self.__authentication_service.get_user(call.from_user.id)
                self.__bot.send_message(5109041126,
                                        f"Ошибка в расписании у курс: {user.get_course()}, группа: {user.get_main_group()}, подгруппа: {user.get_sub_group()} от {call.from_user.username} c id {call.from_user.id}")
                self.__bot.send_message(call.from_user.id,
                                        "Спасибо! Ваша жалоба успешно отправлена, и мои разработчики рассмотрят её в ближайшее время.")
            else:
                self.__bot.send_message(call.from_user.id, "Рады, что все работает хорошо)")

        def handle_error(user_id, error_log, error_text=""):
            error_text = f"⚠️Ошибка⚠️\n\n{error_text}\n\n{error_log}"
            self.__bot.send_message(user_id, error_text)
