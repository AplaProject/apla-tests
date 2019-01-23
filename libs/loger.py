import os
import logging
import inspect


def stack():
    return inspect.stack()


def set_level(level):
    return {
        'NOTSET': logging.NOTSET,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.INFO,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }.get(level)


def create_loger(name, filename='tests.log', console_level='DEBUG', file_level='DEBUG'):
    module_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(module_dir, '..', 'logs', filename)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(console_level)

    fh = logging.FileHandler(log_path)
    fh.setLevel(file_level)

    console_formatter = logging.Formatter(
        '[%(levelname)s] \t %(message)s')

    file_formatter = logging.Formatter(
        '[%(levelname)s] \t %(message)s \t %(module)s:%(name)s:%(funcName)s:%(lineno)s \t %(asctime)s')

    ch.setFormatter(console_formatter)
    fh.setFormatter(file_formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
