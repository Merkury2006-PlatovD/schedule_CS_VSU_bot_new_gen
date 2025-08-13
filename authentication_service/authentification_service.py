import base64
import logging
import secrets
from logging import Logger

import mysql.connector

from authentification_service.util.logger import set_up_logger
from authentification_service.util.error import APIError
from authentification_service.util.error import DatabaseOperationException
from authentification_service.db.interface import AuthenticationConnector


class AuthenticationService:
    __db: AuthenticationConnector
    __logger: Logger

    def __init__(self, database: AuthenticationConnector):
        self.__db = database
        self.__logger = set_up_logger()

    def start_service(self):
        self.__db.init_connection()

    def update_user_data(self, update_type: str, user_id: int, new_data: int):
        if not isinstance(new_data, int):
            raise ValueError("Wrong value type")

        try:
            match update_type:
                case 'course':
                    if 1 <= new_data <= 4:
                        self.__db.update_user_course(user_id, new_data)
                    else:
                        raise ValueError("Wrong course value amount")
                case 'group':
                    if 1 <= new_data <= 18:
                        self.__db.update_user_group(user_id, new_data)
                    else:
                        raise ValueError("Wrong group value amount")
                case 'sub_group':
                    if 1 <= new_data <= 2:
                        self.__db.update_user_subgroup(user_id, new_data)
                    else:
                        raise ValueError("Wrong sub_group value amount")
        except mysql.connector.Error as err:
            self.__logger.warning("Database error in authentication service. %s", err)
            raise err

    def add_user(self, user_id):
        is_success = self.__db.add_new_user_by_id(user_id)
        if not is_success:
            logging.warning(f"Error during creating new user with id {user_id}.")
            raise DatabaseOperationException("No creating user")

    def __generate_api_key(self):
        random_bytes = secrets.token_bytes(32)
        api_key = base64.urlsafe_b64encode(random_bytes).decode("utf-8")
        return api_key

    def add_new_api_key(self, user_id):
        if self.__db.check_api_key_exists_for_user(user_id):
            raise APIError()
        api_key = self.__generate_api_key()
        self.__db.add_new_api_key(user_id, api_key)
        return api_key

    def remove_api_key(self, user_id):
        self.__db.remove_api_key(user_id)

    def has_user(self, user_id):
        return self.__db.check_user_exists(user_id)

    def get_user(self, user_id):
        return self.__db.get_user(user_id)
