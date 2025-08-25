class TooFrequentRequestException(Exception):
    """Слишком частые запросы"""

    def __init__(self, *args):
        self.message = ''
        if args:
            self.message = args[0]

    def __str__(self):
        return f"Ошибка {self.message}"
