import logging
import os

import nonebot
from loguru import logger as loguruLogger
from nonebot.log import logger as botLogger
from quart import Quart

from utils.botConfig import convertSettingsToDict, settings

os.chdir(os.path.split(__file__)[0])
LOG_FILE_DIR = './data/logs'

if not os.path.exists(LOG_FILE_DIR):
    os.mkdir(LOG_FILE_DIR)


class _LoguruHandler(logging.Handler):
    def emit(self, record):
        message = record.getMessage()
        logger = loguruLogger
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, message)


def initApp() -> Quart:
    assert nonebot.scheduler  #Check if scheduler exists
    #Initialize logging
    loggingPath = os.path.join(LOG_FILE_DIR, '{time}.log')
    loguruHandler = _LoguruHandler()
    loguruLogger.add(loggingPath, enqueue=True, encoding='utf-8')
    botLogger.handlers.clear()
    botLogger.addHandler(loguruHandler)
    #Initialize settings
    nonebot.init(settings)
    nonebot.load_plugins('plugins', 'plugins')
    nonebot.logger.debug(
        f'The robot is currently configured as: {convertSettingsToDict()}')
    return nonebot.get_bot().asgi
