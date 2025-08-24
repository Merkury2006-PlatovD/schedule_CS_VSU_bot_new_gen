from logging import Logger
from os import getenv

import mysql.connector
from mysql.connector.aio import MySQLConnectionAbstract

from src.authentication_service.util.interface import DataTransferable
from src.authentication_service.model.model import UserDTO
from src.tools.logger import set_up_logger

"""
Сделанно под следующую структуру

CREATE TABLE user(
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    course INT,
    main_group INT,
    sub_group int
);

CREATE TABLE api(
    user_id BIGINT PRIMARY KEY,
    api_key VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);
"""


class DataBase(DataTransferable):
    __connection: MySQLConnectionAbstract | None
    __users_db_name: str
    __api_key_db_name: str
    __logger: Logger

    def __init__(self, connection: MySQLConnectionAbstract):
        self.__connection = connection
        self.__users_db_name = getenv('USERS_TABLE_NAME')
        self.__api_key_db_name = getenv('API_TABLE_NAME')
        self.__logger = set_up_logger('log/authentication.log')

    def check_user_exists(self, user_id: int) -> bool:
        query = f'SELECT user_id FROM {self.__users_db_name} WHERE user_id = %s'
        params = (user_id,)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            self.__logger.warning('Error while check_user_exists(). %s', err.msg)
        return False

    def check_apikey_exists(self, key: str) -> bool:
        query = f"SELECT user_id FROM {self.__api_key_db_name} WHERE api_key=%s"
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
        query = f'INSERT INTO {self.__users_db_name}(user_id, course, main_group, sub_group) VALUES (%s, Null, Null, Null)'
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

    def get_api_key_for_user(self, user_id: int) -> str | None:
        query = f'SELECT api_key FROM {self.__api_key_db_name} WHERE user_id=%s'
        params = (user_id,)
        try:
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except mysql.connector.Error as err:
            self.__logger.warning('Error while remove_api_key(). %s', err)
        return None
