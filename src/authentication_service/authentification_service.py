import base64
import json
import logging
import secrets
from logging import Logger
from os import getenv

import mysql.connector

from src.authentication_service.model.model import UserDTO
from src.authentication_service.db.redis_repo import RedisDatabase
from src.authentication_service.util.error import APIError, NoUserException
from src.authentication_service.util.error import DatabaseOperationException
from src.authentication_service.util.interface import DataTransferable
import redis
from src.tools.logger import set_up_logger


class AuthenticationService:
    __db: DataTransferable
    __redis_db: RedisDatabase
    __logger: Logger

    def __init__(self, database: DataTransferable, redis_init: RedisDatabase):
        self.__db = database
        self.__logger = set_up_logger('log/authentication.log')
        self.__redis_db = redis_init

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

        self.__redis_db.delete_from_cache(db="user", key=user_id)

    def add_user(self, user_id):
        is_success = self.__db.add_new_user_by_id(user_id)
        if not is_success:
            logging.warning(f"Error during creating new user with id {user_id}.")
            raise DatabaseOperationException("No creating user")

    @staticmethod
    def generate_api_key():
        random_bytes = secrets.token_bytes(32)
        api_key = base64.urlsafe_b64encode(random_bytes).decode("utf-8")
        return api_key

    def add_new_api_key(self, user_id):
        if self.__db.check_apikey_exists(user_id):
            raise APIError()
        api_key = self.generate_api_key()
        self.__db.add_new_api_key(user_id, api_key)
        return api_key

    def check_api_key(self, user_id, api_key_given):
        api_key = self.__redis_db.get_from_cache(db="api", key=user_id)
        if api_key is None:
            api_key = self.__db.get_api_key_for_user(user_id)
            if api_key is not None:
                self.__redis_db.set_cache(db="api", key=user_id, value=api_key)
            return api_key_given == api_key
        return api_key == api_key_given

    def has_key(self, key: str):
        return self.__db.check_apikey_exists(key)

    def remove_api_key(self, user_id):
        self.__redis_db.delete_from_cache(db="api", key=user_id)
        try:
            self.__db.remove_api_key(user_id)
        except redis.RedisError as err:
            self.__logger.warning("Redis failed to delete api cache. %s", err)

    def has_user(self, user_id):
        if self.__redis_db.get_from_cache(db="user", key=user_id):
            return True
        return self.__db.check_user_exists(user_id)

    def get_user(self, user_id):
        try:
            data = self.__redis_db.get_from_cache(db="user", key=user_id)
            if data:
                user = UserDTO.create_from_json(data)
                if user:
                    return user

            user = self.__db.get_user(user_id)
            if not user:
                raise NoUserException("At the return statement user variable is null")
            self.__redis_db.set_cache(db="user", key=user_id, value=user.get_data_json(),
                                      exp=int(getenv("REDIS_USER_DATA_SAVE_DURATION")))
            return user
        except json.JSONDecodeError as err:
            self.__logger.warning("Error json parsing while getting user data. %s", err)
        except mysql.connector.Error as err:
            self.__logger.warning("Database error while getting user data. %s", err)
        except NoUserException as err:
            self.__logger.warning("Error no user data. %s", err)
