import logging


def set_up_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    file_handler = logging.FileHandler('./log/authentication.log')
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)
    return logger
