LOG_DIR = './data/logs'


def _getLogName():
    import os
    from datetime import datetime
    date = str(datetime.now()).replace(':', '_')
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    return os.path.join(LOG_DIR, f'{date}.log')


def _initApp():
    import nonebot
    from nonebot import logger
    from quart import Quart
    from logging import FileHandler, Formatter
    from utils.botConfig import convertSettingsToDict, settings
    _logFormatter = Formatter(
        '[%(asctime)s %(name)s] %(levelname)s: %(message)s')
    _logHandler = FileHandler(filename=_getLogName(), encoding='utf-8')
    _logHandler.setFormatter(_logFormatter)
    logger.addHandler(_logHandler)
    nonebot.init(settings)
    nonebot.load_plugins('plugins', 'plugins')
    logger.debug(f'The robot is currently set to:{convertSettingsToDict()}')
    return nonebot.get_bot().asgi


app = _initApp()
