from time import time

from colorama import init as colorInit

from utils.exception import ExceptionProcess

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

Copyright © 2019-2020 mnixry,All Rights Reserved
Project: https://github.com/mnixry/coolQPythonBot
=================================================''' + '\033[0m'

if __name__ == "__main__":
    print(COPYRIGHT)
    import nonebot
    from app import initApp
    app = initApp()
    startTime = time()
    try:
        nonebot.run()
    except KeyboardInterrupt:
        nonebot.logger.fatal('Program stopped due to user termination.' +
                             f'Uptime:{round(time() - startTime,3)}s')
    finally:
        nonebot.logger.fatal(
            'The program encountered a fatal error and exited unexpectedly.' +
            f' Tracking ID: {ExceptionProcess.catch()}')