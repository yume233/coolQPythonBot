import logging
import os

from loguru import logger
from nonebot.log import logger as botLogger

LOG_DIR = './data/logs'

if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)


class _LoguruHandler(logging.Handler):
    def emit(self, record):
        message = record.getMessage()
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, message)


logger.add(os.path.join(LOG_DIR, '{time}.log'), enqueue=True, encoding='utf-8')
botLogger.handlers.clear()
botLogger.addHandler(_LoguruHandler())
