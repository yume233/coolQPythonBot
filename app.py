import nonebot
from quart import Quart

from utils.log import logger
from utils.settings.bot import convertSettingsToDict, settings


def initApp()->Quart:
    nonebot.init(settings)
    nonebot.load_plugins('plugins','plugins')
    logger.debug(f'The robot is currently configured as: {convertSettingsToDict()}')
    return nonebot.get_bot().asgi
