import os

import nonetrip
from nonebot.log import logger as botLogger

from utils.botConfig import convertSettingsToDict, settings

os.chdir(os.path.split(__file__)[0])
LOG_FILE_DIR = "./data/logs"

if not os.path.exists(LOG_FILE_DIR):
    os.mkdir(LOG_FILE_DIR)


def initApp():
    assert nonetrip.scheduler  # Check if scheduler exists
    # Initialize logging
    loggingPath = os.path.join(LOG_FILE_DIR, "{time}.log")
    botLogger.add(loggingPath, enqueue=True, encoding="utf-8")
    # Initialize settings
    nonetrip.init(settings)
    nonetrip.load_plugins("plugins", "plugins")
    botLogger.info(f"The robot is currently configured as: {convertSettingsToDict()}")
    bot = nonetrip.get_bot()
    return bot.asgi
