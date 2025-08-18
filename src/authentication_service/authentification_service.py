import base64
import logging
import secrets
from logging import Logger

import mysql.connector
import redis
from redis import Redis

from src.authentication_service.util.error import APIError
from src.authentication_service.util.error import DatabaseOperationException
from src.authentication_service.db.interface import AuthenticationConnector
from src.tools_wrappers.logger import set_up_logger
from src.tools_wrappers.redis_wrapper import RedisWrapper


class AuthenticationService:
    __db: AuthenticationConnector
    __redis: Redis
    __logger: Logger

    def __init__(self, database: AuthenticationConnector):
        self.__db = database
        self.__logger = set_up_logger('log/authentication.log')
        self.__redis = RedisWrapper.get_redis()

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

        try:
            self.__redis.delete(f"user:{user_id}")
        except redis.RedisError as err:
            self.__logger.warning("Redis failed to delete user cache. %s", err)

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

    def check_api_key(self, user_id, api_key):
        if self.__redis.get(f"api:{user_id}") is None:
            return self.__db.get_api_key_for_user(user_id) == api_key
        elif self.__redis.get(f"api:{user_id}") == api_key:
            return True
        else:
            return False

    def has_key(self, key: str):
        return self.__db.check_apikey_exists(key)

    def remove_api_key(self, user_id):
        self.__redis.delete(f"api:{user_id}")
        try:
            self.__db.remove_api_key(user_id)
        except redis.RedisError as err:
            self.__logger.warning("Redis failed to delete api cache. %s", err)

    def has_user(self, user_id):
        if self.__redis.get(f"user:{user_id}"):
            return True
        return self.__db.check_user_exists(user_id)

    def get_user(self, user_id):
        user = self.__redis.get(f"user:{user_id}")
        if user:
            return user

        user = self.__db.get_user(user_id)
        if not user:
            return None
        self.__redis.set(f"user:{user_id}", user.get_data_json(), ex=RedisWrapper.USER_SAVING_DURAtION)
        return user
