class DatabaseOperationException(Exception):
    """Ошибка операции в БД"""

    def __init__(self, *args):
        self.message = ''
        if args:
            self.message = args[0]

    def __str__(self):
        return f"Ошибка {self.message}"


class APIError(Exception):
    """Ошибка работы с API"""

    def __init__(self, *args):
        self.message = args[0]

    def __str__(self):
        return f"Ошибка {self.message}"
