import json


class UserDTO:
    def __init__(self, user_id, course, main_group, sub_group):
        self.__user_id = user_id
        self.__course = course
        self.__main_group = main_group
        self.__sub_group = sub_group

    def __str__(self):
        return f'Пользователь с id={self.__user_id} с {self.__course} курса из {self.__main_group} группы {self.__sub_group} подгруппы'

    def get_user_id(self):
        return self.__user_id

    def get_course(self):
        return self.__course

    def get_main_group(self):
        return self.__main_group

    def get_sub_group(self):
        return self.__sub_group

    def get_data_json(self):
        return json.dumps({
            'user_id': self.__user_id,
            'course': self.__course,
            'main_group': self.__main_group,
            'sub_group': self.__sub_group
        })

    @classmethod
    def create_from_json(cls, json_data):
        (user_id, course, main_group, subgroup) = json.loads(json_data).values()
        return UserDTO(int(user_id), int(course), int(main_group), int(subgroup))


class RequestDTO:
    def __init__(self, user_id: int, timing: int, tokens: int):
        self.__user_id = user_id
        self.__timing = timing
        self.__tokens = tokens

    def get_user_id(self):
        return self.__user_id

    def set_timing(self, timing: int):
        self.__timing = timing

    def get_timing(self):
        return self.__timing

    def get_tokens(self):
        return self.__tokens

    def set_tokens(self, cnt: int):
        self.__tokens = cnt

    def decrease_tokens(self):
        self.__tokens = 0 if self.__tokens - 1 < 0 else self.__tokens - 1

    def get_data_json(self):
        return json.dumps({
            'user_id': self.__user_id,
            'timing': self.__timing,
            'tokens': self.__tokens,
        })

    @classmethod
    def create_from_json(cls, json_data):
        (user_id, timing, tokens) = json.loads(json_data).values()
        return RequestDTO(int(user_id), int(timing), int(tokens))
