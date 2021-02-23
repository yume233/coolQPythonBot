from time import time

import nonebot
from colorama import init as colorInit
from nonebot import logger
from nonebot.adapters.cqhttp import Bot

from utils.botConfig import convertSettingsToDict

colorInit()

COPYRIGHT = (
    "\033[0;37;1m"
    + r"""
                     _  _____ ______         _    _                   ______         _
                    | ||  _  || ___ \       | |  | |                  | ___ \       | |
  ___   ___    ___  | || | | || |_/ / _   _ | |_ | |__    ___   _ __  | |_/ /  ___  | |_
 / __| / _ \  / _ \ | || | | ||  __/ | | | || __|| '_ \  / _ \ | '_ \ | ___ \ / _ \ | __|
| (__ | (_) || (_) || |\ \/' /| |    | |_| || |_ | | | || (_) || | | || |_/ /| (_) || |_
 \___| \___/  \___/ |_| \_/\_\\_|     \__, | \__||_| |_| \___/ |_| |_|\____/  \___/  \__|
                                       __/ |
                                      |___/

Copyright © 2019-2020 mnixry,All Rights Reserved
Project: https://github.com/mnixry/coolQPythonBot
================================================="""
    + "\033[0m"
)

nonebot.init(**{k.lower(): v for k, v in convertSettingsToDict().items()})
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("nonetrip")
nonebot.load_plugins("ELF_RSS/src/plugins")
nonebot.get_driver().register_adapter("cqhttp", Bot)

if __name__ == "__main__":
    print(COPYRIGHT)

    from app import initApp

    app = initApp()
    startTime = time()

    from utils.exception import ExceptionProcess

    try:
        nonebot.run()
    except KeyboardInterrupt:
        logger.critical(
            "Program stopped due to user termination."
            + f"Uptime:{time() - startTime:.3f}s"
        )
    finally:
        logger.critical(
            "The program encountered a fatal error and exited unexpectedly."
            + f" Tracking ID: {ExceptionProcess.catch()}"
        )
