import nonebot
from colorama import init as colorInit
from nonebot import logger

from utils import initialization
from utils.botConfig import convertSettingsToDict, settings

colorInit()

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
''' + '\033[0m'

if __name__ == "__main__":
    print(COPYRIGHT)
    nonebot.init(settings)
    nonebot.load_plugins('plugins', 'plugins')
    initialization.start(nonebot.get_bot())
    logger.debug(f'Settings:{convertSettingsToDict()}')
    nonebot.run()
