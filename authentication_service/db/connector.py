from logging import Logger

import mysql.connector
from mysql.connector.aio import MySQLConnectionAbstract
from starlette.config import environ

from authentication_service.db.interface import AuthenticationConnector
from authentication_service.db.model import UserDTO
from authentication_service.util.logger import set_up_logger

"""
Сделанно под следующую структуру

CREATE TABLE user(
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    course INT,
    main_group INT,
    sub_group int
)

CREATE TABLE api(
    user_id INT PRIMARY KEY,
    api_key VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);
"""


class DataBase(AuthenticationConnector):
    __instance = None

    __connection: MySQLConnectionAbstract | None
    __users_db_name: str
    __api_key_db_name: str
    __logger: Logger

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def init_connection(self):
        self.__get_init_vars()
        max_attempt_cnt = int(environ.get('DB_CONNECTION_ATTEMPTS'))
        attempt = 0
        while attempt < max_attempt_cnt:
            try:
                self.__connection = mysql.connector.connect(
                    user=environ.get('DB_USER'),
                    password=environ.get('DB_USER_PASSWORD'),
                    host=environ.get('DB_HOST'),
                    database=environ.get('DB_NAME')
                )
            except (mysql.connector.Error, IOError) as err:
                if attempt + 1 == max_attempt_cnt:
                    self.__logger.error('Failed to connect to database. Exiting without __connection. %s', err)
                    raise mysql.connector.Error
                self.__logger.warning('Failed __connection attempt. Trying to reconnect. Remaining %d tries',
                                      max_attempt_cnt - attempt)
            attempt += 1
        self.__logger.info('Successfully connected to database')

    def reconnect(self) -> None:
        self.__connection = None
        self.init_connection()

    # @staticmethod
    # def __check_connection(func):
    #     @wraps(func)
    #     def _wrapper(self, *args, **kwargs):
    #         if self.__connection is None or not self.__connection.is_connected():
    #             self.__reconnect()
    #         return func()
    #
    #     return _wrapper

    def __get_init_vars(self):
        self.__users_db_name = environ.get('USERS_TABLE_NAME')
        self.__api_key_db_name = environ.get('API_TABLE_NAME')
        self.__logger = set_up_logger()

    def close_connection(self):
        self.__connection.close()
        del self.__connection

    def check_user_exists(self, user_id: int) -> bool:
        query = f'SELECT user_id FROM {self.__users_db_name} WHERE user_id = %s'
        params = (user_id,)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            self.__logger.warning('Error while check_user_exists(). %s', err)
        return False

    def check_apikey_exists(self, key: str) -> bool:
        query = f"SELECT user_id FROM {self.__users_db_name} INNER JOIN {self.__api_key_db_name} USING(user_id) WHERE api_key='%s'"
        params = (key,)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            self.__logger.warning('Error while check_apikey_exists(). %s', err)
        return False

    def get_user(self, user_id: int) -> UserDTO | None:
        query = f'SELECT * FROM {self.__users_db_name} WHERE user_id=%s'
        params = (user_id,)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                (user_id, course, main_group, sub_group) = cursor.fetchall()[0]
                return UserDTO(user_id, course, main_group, sub_group)
        except mysql.connector.Error as err:
            self.__logger.warning('Error while get_user(). %s', err)
        return None

    def add_new_user_by_id(self, user_id: int) -> bool:
        query = f'INSERT INTO {self.__users_db_name}(user_id, course, main_group, sub_group) VALUE (%s, Null, Null, Null)'
        params = (user_id,)
        try:
            if not isinstance(user_id, int):
                raise ValueError('Wrong id type!')
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                self.__connection.commit()
                return True
        except mysql.connector.Error as err:
            self.__logger.warning('Error while add_new_user_by_id(). %s', err)
        except ValueError as err:
            self.__logger.warning('Error while add_new_user_by_id(). %s', err)
        return False

    def update_user_course(self, user_id: int, course: int) -> bool:
        query = f'UPDATE {self.__users_db_name} SET course=%s WHERE user_id=%s'
        params = (course, user_id)
        try:
            if not isinstance(course, int):
                raise ValueError('Wrong course type!')
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                return True
        except mysql.connector.Error as err:
            self.__logger.warning('Error while update_user_course(). %s', err)
        except ValueError as err:
            self.__logger.warning('Error while update_user_course(). %s', err)
        return False

    def update_user_group(self, user_id: int, main_group: int) -> bool:
        query = f'UPDATE {self.__users_db_name} SET main_group=%s WHERE user_id=%s'
        params = (main_group, user_id)
        try:
            if not isinstance(main_group, int):
                raise ValueError('Wrong group type!')
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                self.__connection.commit()
                return True
        except mysql.connector.Error as err:
            self.__logger.warning('Error while update_user_group(). %s', err)
        except ValueError as err:
            self.__logger.warning('Error while update_user_group(). %s', err)
        return False

    def update_user_subgroup(self, user_id: int, sub_group: int) -> bool:
        query = f'UPDATE {self.__users_db_name} SET sub_group=%s WHERE user_id=%s'
        params = (sub_group, user_id)
        try:
            if not isinstance(sub_group, int):
                raise ValueError('Wrong sub_group type!')
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                self.__connection.commit()
                return True
        except mysql.connector.Error as err:
            self.__logger.warning('Error while update_user_sub_group(). %s', err)
        except ValueError as err:
            self.__logger.warning('Error while update_user_sub_group(). %s', err)
        return False

    def add_new_api_key(self, user_id: int, api_key_value: str) -> bool:
        query = f'INSERT INTO {self.__api_key_db_name}(user_id, api_key) VALUE (%s, %s)'
        params = (user_id, api_key_value)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                self.__connection.commit()
                return True
        except mysql.connector.Error as err:
            self.__logger.warning('Error while add_new_api_key(). %s', err)
        return False

    def remove_api_key(self, user_id: int) -> bool:
        query = f'DELETE FROM {self.__api_key_db_name} WHERE user_id=%s'
        params = (user_id,)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                self.__connection.commit()
                return True
        except mysql.connector.Error as err:
            self.__logger.warning('Error while remove_api_key(). %s', err)
        return False

    def check_api_key_exists_for_user(self, user_id: int) -> bool:
        query = f'SELECT user_id FROM {self.__api_key_db_name} INNER JOIN {self.__users_db_name} USING(user_id) WHERE user_id=%s'
        params = (user_id,)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            self.__logger.warning('Error while check_api_key_exists_for_user(). %s', err)
        return False
