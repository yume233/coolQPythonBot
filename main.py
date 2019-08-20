import nonebot
from nonebot import logger

from utils import initialization
from utils.botConfig import getSettings, settings

if __name__ == "__main__":
    nonebot.init(settings)
    nonebot.load_plugins('plugins', 'plugins')
    initialization.start(nonebot.get_bot())
    logger.debug(f'Settings:{getSettings()}')
    nonebot.run()
