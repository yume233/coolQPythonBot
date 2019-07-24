import nonebot
from nonebot import logger
from utils.botConfig import settings,getSettings

if __name__ == "__main__":
    nonebot.init(settings)
    nonebot.load_plugins('plugins', 'plugins')
    logger.debug(f'Settings:{getSettings()}')
    nonebot.run()