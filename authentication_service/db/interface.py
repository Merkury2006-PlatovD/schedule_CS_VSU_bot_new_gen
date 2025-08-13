from abc import ABC, abstractmethod

from authentication_service.db.model import UserDTO


class DatabaseConnectable(ABC):
    @abstractmethod
    def init_connection(self) -> None: pass

    @abstractmethod
    def close_connection(self) -> None: pass

    @abstractmethod
    def reconnect(self) -> None: pass


class DataTransferable(ABC):
    @abstractmethod
    def check_user_exists(self, user_id: int) -> bool: pass

    @abstractmethod
    def check_apikey_exists(self, key: str) -> bool: pass

    @abstractmethod
    def get_user(self, user_id: int) -> UserDTO | None: pass

    @abstractmethod
    def add_new_user_by_id(self, user_id: int) -> bool: pass

    @abstractmethod
    def update_user_course(self, user_id: int, course: int) -> bool: pass

    @abstractmethod
    def update_user_group(self, user_id: int, main_group: int) -> bool: pass

    @abstractmethod
    def update_user_subgroup(self, user_id: int, sub_group: int) -> bool: pass

    @abstractmethod
    def add_new_api_key(self, user_id: int, api_key_value: str) -> bool: pass

    @abstractmethod
    def remove_api_key(self, user_id: int) -> bool: pass

    @abstractmethod
    def check_api_key_exists_for_user(self, user_id: int) -> bool: pass


class AuthenticationConnector(DatabaseConnectable, DataTransferable, ABC):
    pass
