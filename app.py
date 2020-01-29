import os
from datetime import datetime
from logging import FileHandler, Formatter

import nonebot
from quart import Quart

from utils.botConfig import convertSettingsToDict, settings

LOG_DIR = './data/logs'

os.chdir(os.path.split(__file__)[0])


def _getLogName():
    date = str(datetime.now()).replace(':', '_')
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    return os.path.join(LOG_DIR, f'{date}.log')


def initApp() -> Quart:
    assert nonebot.scheduler
    _logFormatter = Formatter(
        '[%(asctime)s %(name)s] %(levelname)s: %(message)s')
    _logHandler = FileHandler(filename=_getLogName(), encoding='utf-8')
    _logHandler.setFormatter(_logFormatter)
    nonebot.logger.addHandler(_logHandler)
    nonebot.init(settings)
    nonebot.load_plugins('plugins', 'plugins')
    nonebot.logger.debug(
        f'The robot is currently configured as: {convertSettingsToDict()}')
    return nonebot.get_bot().asgi
