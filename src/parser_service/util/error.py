class ParserError(Exception):
    pass


class ScheduleParserFindError(ParserError):
    def __init__(self, *args):
        self.message = ''
        if args:
            self.message = args[0]

    def __str__(self):
        return f"Ошибка поиска нужных данных. {self.message}"

class NotFoundListError(ParserError):
    def __init__(self, *args):
        self.message = ''
        if args:
            self.message = args[0]

    def __str__(self):
        return f"Ошибка поиска листа для парсинга. {self.message}"

class NoReserveFileError(ParserError):
    def __init__(self, *args):
        self.message = ''
        if args:
            self.message = args[0]

    def __str__(self):
        return f"Резервный файл отсутсвует. {self.message}"