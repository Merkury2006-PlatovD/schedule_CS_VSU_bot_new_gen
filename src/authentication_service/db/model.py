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
        try:
            (user_id, course, main_group, subgroup) = json.loads(json_data).values()
            return UserDTO(user_id, int(course), int(main_group), int(subgroup))
        except json.JSONDecodeError:
            return None
