from os import environ
from typing import Any
from mysql.connector import MySQLConnection
import mysql.connector

from src.authentication_service.util.interface import DatabaseConnectable


class DBConnector(DatabaseConnectable):
    __db: MySQLConnection | Any = None

    @classmethod
    def init_connection(cls) -> None:
        cls.__get_init_vars()
        max_attempt_cnt = int(environ.get('DB_CONNECTION_ATTEMPTS'))
        attempt = 0
        while attempt < max_attempt_cnt:
            try:
                cls.__db = mysql.connector.connect(
                    user=environ.get('DB_USER'),
                    password=environ.get('DB_USER_PASSWORD'),
                    host=environ.get('DB_HOST'),
                    database=environ.get('DB_NAME'),
                )
            except (mysql.connector.Error, IOError) as err:
                if attempt + 1 == max_attempt_cnt:
                    raise mysql.connector.Error
            attempt += 1

    @classmethod
    def __get_init_vars(cls):
        cls.__users_db_name = environ.get('USERS_TABLE_NAME')
        cls.__api_key_db_name = environ.get('API_TABLE_NAME')

    @classmethod
    def get_connection(cls) -> Any:
        return cls.__db

    @classmethod
    def close_connection(cls) -> None:
        cls.__db.close()

    @classmethod
    def reconnect(cls) -> None:
        cls.__db = None
        cls.init_connection()
