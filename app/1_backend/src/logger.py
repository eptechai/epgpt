import logging

format = "[%(asctime)s] [%(levelname)s] [%(name)s] (%(filename)s:%(funcName)s@%(lineno)s): %(message)s"
formatter = logging.Formatter(fmt=format)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


def create_logger(name: str):
    """
    Creates a logger with the given name.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    return logger


def configure_format(logger_name):
    logger = logging.getLogger(logger_name)
    logger.propagate = True
    return logger