class UserDTO:
    def __init__(self, user_id, course, group, subgroup):
        self.__user_id = user_id
        self.__course = course
        self.__main_group = group
        self.__sub_group = subgroup

    def __str__(self):
        return f'Пользователь с id={self.__user_id} с {self.__course} курса из {self.__main_group} группы {self.__sub_group} подгруппы'

    def get_user_id(self):
        return self.__user_id

    def get_course(self):
        return self.__course

    def get_group(self):
        return self.__main_group

    def get_subgroup(self):
        return self.__sub_group
