import nonebot
from colorama import init as colorInit
from nonebot import logger
from time import time
from datetime import datetime
import os

from logging import FileHandler, Formatter
from utils.botConfig import convertSettingsToDict, settings
from utils.exception import CatchException

colorInit()

LOG_DIR = './data/logs'
COPYRIGHT = '\033[0;37;1m' + r'''
                     _  _____ ______         _    _                   ______         _   
                    | ||  _  || ___ \       | |  | |                  | ___ \       | |  
  ___   ___    ___  | || | | || |_/ / _   _ | |_ | |__    ___   _ __  | |_/ /  ___  | |_ 
 / __| / _ \  / _ \ | || | | ||  __/ | | | || __|| '_ \  / _ \ | '_ \ | ___ \ / _ \ | __|
| (__ | (_) || (_) || |\ \/' /| |    | |_| || |_ | | | || (_) || | | || |_/ /| (_) || |_ 
 \___| \___/  \___/ |_| \_/\_\\_|     \__, | \__||_| |_| \___/ |_| |_|\____/  \___/  \__|
                                       __/ |                                             
                                      |___/                                              

Copyright © 2019 mnixry,All Rights Reserved
Project: https://github.com/mnixry/coolQPythonBot
=================================================''' + '\033[0m'


def _getLogName():
    date = str(datetime.now()).replace(':', '_')
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    return os.path.join(LOG_DIR, f'{date}.log')


_logFormatter = Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')
_logHandler = FileHandler(filename=_getLogName(), encoding='utf-8')
_logHandler.setFormatter(_logFormatter)
logger.addHandler(_logHandler)

if __name__ == "__main__":
    print(COPYRIGHT)
    nonebot.init(settings)
    nonebot.load_plugins('plugins', 'plugins')
    logger.debug(f'The robot is currently set to:{convertSettingsToDict()}')
    startTime = time()
    try:
        nonebot.run()
    except KeyboardInterrupt:
        logger.fatal('Program stopped due to user termination.' +
                     f'Uptime:{round(time() - startTime,3)}s')
    finally:
        logger.fatal(
            'The program encountered a fatal error and exited unexpectedly.' +
            f' Tracking ID: {CatchException()}')